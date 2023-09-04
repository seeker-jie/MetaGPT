#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/7/4 10:53
@Author  : alexanderwu
@File    : mermaid.py
@Modified By: mashenquan, 2023/8/20. Remove global configuration `CONFIG`, enable configuration support for business isolation.
"""
import asyncio
from pathlib import Path

# from metagpt.utils.common import check_cmd_exists
import aiofiles

from metagpt.config import CONFIG, Config
from metagpt.const import PROJECT_ROOT
from metagpt.logs import logger


async def mermaid_to_file(mermaid_code, output_file_without_suffix, width=2048, height=2048) -> int:
    """suffix: png/svg/pdf

    :param mermaid_code: mermaid code
    :param output_file_without_suffix: output filename
    :param width:
    :param height:
    :return: 0 if succed, -1 if failed
    """
    # Write the Mermaid code to a temporary file
    tmp = Path(f"{output_file_without_suffix}.mmd")
    async with aiofiles.open(tmp, "w", encoding="utf-8") as f:
        await f.write(mermaid_code)
    # tmp.write_text(mermaid_code, encoding="utf-8")

    # if check_cmd_exists("mmdc") != 0:
    #     logger.warning("RUN `npm install -g @mermaid-js/mermaid-cli` to install mmdc")
    #     return -1

    # for suffix in ["pdf", "svg", "png"]:
    for suffix in ["png"]:
        output_file = f"{output_file_without_suffix}.{suffix}"
        # Call the `mmdc` command to convert the Mermaid code to a PNG
        logger.info(f"Generating {output_file}..")
        cmds = [CONFIG.mmdc, "-i", str(tmp), "-o", output_file, "-w", str(width), "-H", str(height)]

        if CONFIG.puppeteer_config:
            cmds.extend(["-p", CONFIG.puppeteer_config])
        process = await asyncio.create_subprocess_exec(*cmds)
        await process.wait()
    return process.returncode


if __name__ == "__main__":
    MMC1 = """classDiagram
        class Main {
            -SearchEngine search_engine
            +main() str
        }
        class SearchEngine {
            -Index index
            -Ranking ranking
            -Summary summary
            +search(query: str) str
        }
        class Index {
            -KnowledgeBase knowledge_base
            +create_index(data: dict)
            +query_index(query: str) list
        }
        class Ranking {
            +rank_results(results: list) list
        }
        class Summary {
            +summarize_results(results: list) str
        }
        class KnowledgeBase {
            +update(data: dict)
            +fetch_data(query: str) dict
        }
        Main --> SearchEngine
        SearchEngine --> Index
        SearchEngine --> Ranking
        SearchEngine --> Summary
        Index --> KnowledgeBase"""

    MMC2 = """sequenceDiagram
        participant M as Main
        participant SE as SearchEngine
        participant I as Index
        participant R as Ranking
        participant S as Summary
        participant KB as KnowledgeBase
        M->>SE: search(query)
        SE->>I: query_index(query)
        I->>KB: fetch_data(query)
        KB-->>I: return data
        I-->>SE: return results
        SE->>R: rank_results(results)
        R-->>SE: return ranked_results
        SE->>S: summarize_results(ranked_results)
        S-->>SE: return summary
        SE-->>M: return summary"""

    conf = Config()
    asyncio.run(
        mermaid_to_file(
            options=conf.runtime_options, mermaid_code=MMC1, output_file_without_suffix=PROJECT_ROOT / "tmp/1.png"
        )
    )
    asyncio.run(
        mermaid_to_file(
            options=conf.runtime_options, mermaid_code=MMC2, output_file_without_suffix=PROJECT_ROOT / "tmp/2.png"
        )
    )
