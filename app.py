from fastapi import FastAPI, Query
from typing import Dict, List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Growth Report Aggregator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

memory_store: Dict[str, List[Dict[str, str]]] = {}


@app.get("/")
def health_check():
    return {"ok": True, "message": "growth report aggregator is running"}


@app.post("/append_growth_material")
def append_growth_material(
    batch_id: str = Query(...),
    link: str = Query(...),
    content: str = Query(...)
):
    batch_id = batch_id.strip()
    link = link.strip()
    content = content.strip()

    if not batch_id:
        return {"ok": False, "error": "batch_id is required"}

    if not link:
        return {"ok": False, "error": "link is required"}

    if not content:
        return {"ok": False, "error": "content is required"}

    if batch_id not in memory_store:
        memory_store[batch_id] = []

    existing_links = {item["link"] for item in memory_store[batch_id]}
    if link not in existing_links:
        memory_store[batch_id].append({
            "link": link,
            "content": content
        })

    return {
        "ok": True,
        "batch_id": batch_id,
        "count": len(memory_store[batch_id])
    }


@app.post("/aggregate_growth_materials")
def aggregate_growth_materials(
    batch_id: str = Query(...),
    extra_notes: str = Query("")
):
    batch_id = batch_id.strip()
    extra_notes = extra_notes.strip()

    if not batch_id:
        return {"ok": False, "error": "batch_id is required"}

    docs = memory_store.get(batch_id, [])

    if not docs:
        return {
            "ok": False,
            "error": "no documents found for this batch_id"
        }

    merged_parts = []
    merged_parts.append(f"【批次ID】\n{batch_id}\n")

    if extra_notes:
        merged_parts.append(f"【补充说明】\n{extra_notes}\n")

    merged_parts.append("【材料正文汇总】\n")

    for idx, doc in enumerate(docs, start=1):
        merged_parts.append(f"### 材料 {idx}")
        merged_parts.append(f"链接：{doc['link']}")
        merged_parts.append("正文：")
        merged_parts.append(doc["content"])
        merged_parts.append("")

    merged_content = "\n".join(merged_parts)

    return {
        "ok": True,
        "batch_id": batch_id,
        "doc_count": len(docs),
        "merged_content": merged_content
    }