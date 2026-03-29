from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import tempfile
from fpdf import FPDF
from pipeline import run_agentic_pipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    ticker: str


class PDFRequest(BaseModel):
    ticker: str
    company_name: str
    current_price: float
    ai_report: str


@app.post("/api/analyze")
def analyze_company(req: AnalyzeRequest):
    try:
        # 这里调用的是你之前稳定版的 pipeline.py
        result = run_agentic_pipeline(req.ticker)
        return {"status": "success", "data": result}
    except Exception as e:
        print(f"❌ [ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export_pdf")
def export_pdf(req: PDFRequest):
    """【黑科技】将 AI 报告瞬间排版成投行级 PDF 文件"""
    try:
        pdf = FPDF()
        pdf.add_page()

        # 设置字体 (FPDF 内置支持常规英文字体)
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, f"Strategic Advisory Report: {req.ticker.upper()}", new_x="LMARGIN", new_y="NEXT", align="C")

        pdf.set_font("helvetica", "I", 12)
        pdf.cell(0, 10, f"Company: {req.company_name} | Current Price: ${req.current_price}", new_x="LMARGIN",
                 new_y="NEXT", align="C")
        pdf.ln(10)

        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "AI Synthesis & Market Context", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        pdf.set_font("helvetica", "", 11)
        # 清理文本以适应 PDF
        clean_report = req.ai_report.replace('\n\n', '\n').encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, clean_report)

        # 写入临时文件并返回
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_file.name)

        return FileResponse(path=temp_file.name, filename=f"{req.ticker}_Report.pdf", media_type='application/pdf')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))