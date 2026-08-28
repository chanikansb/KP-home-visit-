import streamlit as st
import requests
import json
import os
import pandas as pd
from datetime import datetime, time
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="ระบบบันทึกและประเมินผลการเยี่ยมบ้านสหวิชาชีพ จังหวัดกำแพงเพชร",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database file path (v2 to keep clean compatibility)
DB_FILE = "home_visit_db_v4.json"

# Kamphaeng Phet Health Promoting Hospitals (รพ.สต. จังหวัดกำแพงเพชร)
KPP_HOSPITALS = [
    "รพ.สต.นครชุม (อ.เมือง)",
    "รพ.สต.ไตรตรึงษ์ (อ.เมือง)",
    "รพ.สต.อ่างทอง (อ.เมือง)",
    "รพ.สต.ทรงธรรม (อ.เมือง)",
    "รพ.สต.หนองปลิง (อ.เมือง)",
    "รพ.สต.ท่าขุนราม (อ.เมือง)",
    "รพ.สต.ลานดอกไม้ (อ.เมือง)",
    "รพ.สต.คลองแม่ลาย (อ.เมือง)",
    "รพ.สต.พรานกระต่าย (อ.พรานกระต่าย)",
    "รพ.สต.ท่าไม้ (อ.พรานกระต่าย)",
    "รพ.สต.คลองลาน (อ.คลองลาน)",
    "รพ.สต.คลองน้ำไหล (อ.คลองลาน)",
    "รพ.สต.ขาณุวรลักษบุรี (อ.ขาณุวรลักษบุรี)",
    "รพ.สต.สลกบาตร (อ.ขาณุวรลักษบุรี)",
    "รพ.สต.คลองขลุง (อ.คลองขลุง)",
    "รพ.สต.ท่ามะเขือ (อ.คลองขลุง)",
    "รพ.สต.ลานกระบือ (อ.ลานกระบือ)",
    "รพ.สต.ทรายทองวัฒนา (อ.ทรายทองวัฒนา)",
    "รพ.สต.บึงสามัคคี (อ.บึงสามัคคี)",
    "รพ.สต.ปางศิลาทอง (อ.ปางศิลาทอง)",
    "รพ.สต.โกสัมพีนคร (อ.โกสัมพีนคร)",
    "อื่นๆ (ระบุเอง)"
]

# Helper function to load data
def load_data():
    if not os.path.exists(DB_FILE):
        # Create rich dummy data matching updated Kamphaeng Phet schema
        dummy_data = [
            {
                "hn": "HN-10001",
                "an": "AN-50012",
                "name": "นายสมชาย ใจดี",
                "gender": "ชาย",
                "age": 68,
                "marriage": "คู่",
                "religion": "พุทธ",
                "pcsu": "รพ.สต.นครชุม (อ.เมือง)",
                "diagnosis": "Type 2 Diabetes Mellitus with Hypertension and CKD Stage 3",
                "patient_type": "DM",
                "adl": 12,
                "occupation": "เกษียณ",
                "income": "8000",
                "benefit": "บัตรทอง",
                "address": "12/3 หมู่ 4 ต.นครชุม อ.เมือง จ.กำแพงเพชร",
                "phone": "081-234-5678",
                "caregiver": "นางสมศรี ใจดี (ภรรยา)",
                "underlying": "HT, DM, CKD",
                "drug_allergy": "Penicillin",
                "food_allergy": "ไม่มี",
                "objectives": ["Long-term care", "ติดตามการใช้ยา"],
                "planning_team": ["พยาบาลวิชาชีพ", "เภสัชกร", "แพทย์"],
                "equipment": ["อุปกรณ์วัด V/S", "ข้อมูลแหล่งสนับสนุน"],
                "responsible_phase1": "พย.วิภา นครชุม",
                "genogram": "ครอบครัวขยาย อยู่กับภรรยาและลูกสาว มีประวัติเบาหวานทางกรรมพันธุ์จากมารดา สัมพันธภาพดีคอยช่วยเหลือกัน",
                "visit_date": "2026-08-20",
                "start_time": "09:30",
                "end_time": "10:30",
                "duration": 60,
                "immobility": "เดินได้เองแต่ต้องใช้ไม้เท้าสามขา มีอาการเข่าเสื่อมเล็กน้อย",
                "nutrition": "รับประทานอาหารตรงเวลา ลดหวานมันเค็มตามแพทย์สั่ง",
                "housing": "บ้านปูนชั้นเดียว ไม่มีธรณีประตูสูง ห้องน้ำมีราวจับเรียบร้อย",
                "other_people": "ภรรยาดูแลหลัก มีลูกสาวช่วยเตรียมยาและอาหาร",
                "medication": "รับประทานยาครบตามสั่ง ไม่มีลืมยา จัดยาใส่กล่องแบ่งช่องรายสัปดาห์",
                "examination": "BP 130/82 mmHg, PR 72 bpm, DTX 118 mg/dL แผลกดทับไม่มี",
                "safety": "พื้นบ้านเรียบ ไม่ลื่น แสงสว่างเพียงพอ ทางเดินสะดวกไม่มีสิ่งกีดขวาง",
                "spiritual": "ผู้ป่วยมีกำลังใจดีมาก ไปทำบุญที่วัดใกล้บ้านเดือนละครั้ง",
                "service": "ประสานงานกับ รพ.สต. เพื่อจัดหาผ้าอ้อมผู้ใหญ่ทางสิทธิ์บัตรทอง",
                "responsible_phase2": "พย.สมศรี นครชุม",
                "triage": {
                    "physical_score": 1, "physical_desc": "มีความดันสูงและเบาหวานแต่ควบคุมได้ดี", "physical_team": ["พยาบาล", "แพทย์"],
                    "psychological_score": 0, "psychological_desc": "ปรับตัวกับโรคเรื้อรังได้ดี ไม่มีภาวะซึมเศร้า", "psychological_team": ["พยาบาล"],
                    "social_score": 0, "social_desc": "ผู้ดูแลมีความพร้อมและใส่ใจดี", "social_team": ["ชุมชน"],
                    "environment_score": 0, "environment_desc": "บ้านปลอดภัย ปรับปรุงสภาวะแวดล้อมแล้ว", "environment_team": ["ชุมชน"],
                    "nutrition_score": 1, "nutrition_desc": "คุมอาหารรสจัดได้ค่อนข้างดี แต่ต้องกระตุ้นน้ำดื่มเพิ่ม", "nutrition_team": ["นักโภชนาการ"]
                },
                "care_plans": [
                    {
                        "date": "2026-08-20",
                        "problem": "เสี่ยงต่อระดับน้ำตาลในเลือดผันผวนเนื่องจากผู้ป่วยขอบทานผลไม้รสหวาน",
                        "goal": "ระดับน้ำตาล DTX อยู่ระหว่าง 80-130 mg/dL",
                        "management": "แนะนำผู้ป่วยหลีกเลี่ยงผลไม้หวานจัด เช่น ทุเรียน ลำไย และเน้นทานฝรั่ง แอปเปิ้ลเขียวแทน",
                        "evaluation": "ทำได้"
                    }
                ],
                "responsible_phase3": "พย.นภาพร ใจดี",
                "active_problems": "พฤติกรรมการรับประทานผลไม้หวานบางครั้ง",
                "non_active_problems": "ความสับสนในการทานยารอบเย็น (แก้ไขได้แล้วโดยจัดกล่องยา)",
                "future_plans": [
                    {
                        "date": "2026-09-20",
                        "topic": "ติดตามระดับน้ำตาลหลังอาหารและประเมินพฤติกรรมบริโภคผลไม้",
                        "goal": "DTX < 140 mg/dL",
                        "team_action": "พยาบาลและนักโภชนาการเข้าตรวจวัดและประเมินซ้ำ",
                        "evaluation": "รอนัดหมาย"
                    }
                ],
                "doctor_name": "นพ.ประวิทย์ รักดี",
                "doctor_note": "ควบคุมสัญญาณชีพได้ดี ให้ตรวจเลือดติดตามค่าไตในอีก 3 เดือนข้างหน้าตามนัดหมายเดิม",
                "nursing_outcome": "ผู้ป่วยสามารถที่จะดูแลตนเองได้",
                "nursing_note": "ผู้ป่วยให้ความร่วมมือดีมาก ผู้ดูแลมีความรู้ความเข้าใจในวิธีการดูแลพยุงและจัดการยา"
            },
            {
                "hn": "HN-10002",
                "an": "AN-50035",
                "name": "นางมาลี รักสงบ",
                "gender": "หญิง",
                "age": 75,
                "marriage": "หม้าย",
                "religion": "พุทธ",
                "pcsu": "รพ.สต.ไตรตรึงษ์ (อ.เมือง)",
                "diagnosis": "Ischemic Stroke with Right Hemiparesis and Stage 2 Pressure Injury",
                "patient_type": "stroke",
                "adl": 4,
                "occupation": "ไม่ได้ทำงาน",
                "income": "600",
                "benefit": "บัตรทอง",
                "address": "45 หมู่ 2 ต.ไตรตรึงษ์ อ.เมือง จ.กำแพงเพชร",
                "phone": "089-876-5432",
                "caregiver": "นายสมคิด รักสงบ (บุตรชาย)",
                "underlying": "HT, Old CVA",
                "drug_allergy": "ไม่มี",
                "food_allergy": "ไม่มี",
                "objectives": ["Long-term care", "ติดตามแผล"],
                "planning_team": ["พยาบาลวิชาชีพ", "นักกายภาพบำบัด", "แหล่งช่วยเหลือสนับสนุนอื่นๆ"],
                "equipment": ["อุปกรณ์วัด V/S", "อุปกรณ์ทำแผล", "อุปกรณ์ทางการแพทย์เฉพาะตัว"],
                "responsible_phase1": "พย.สมศรี ไตรตรึงษ์",
                "genogram": "อาศัยอยู่กับบุตรชายที่เป็นผู้ดูแลหลัก สามีเสียชีวิตแล้ว ความสัมพันธ์ค่อนข้างเครียดเนื่องจากภาระค่าใช้จ่ายและเวลาดูแล",
                "visit_date": "2026-08-25",
                "start_time": "13:00",
                "end_time": "14:15",
                "duration": 75,
                "immobility": "ผู้ป่วยติดเตียง ขยับแขนและขาด้านซ้ายได้เล็กน้อย ด้านขวาอ่อนแรงสมบูรณ์",
                "nutrition": "ให้อาหารทางสายยาง (NG Tube) สูตรมาตรฐาน ป้อนวันละ 4 มื้อ",
                "housing": "บ้านไม้ใต้ถุนสูง ห้องนอนผู้ป่วยอยู่ชั้นล่าง แสงสว่างปานกลาง มีลมโกรก",
                "other_people": "ลูกชายทำงานพาร์ทไทม์ ทำให้บางครั้งต้องทิ้งผู้ป่วยไว้คนเดียวในช่วงสั้นๆ",
                "medication": "ยาบดให้ทางสายยาง ทานครบตามกำหนด",
                "examination": "BP 120/75 mmHg, PR 68 bpm, BT 36.5C มีแผลกดทับที่สะโพกขนาด 2x2 ซม. ระดับ 2 คลีนิกดี",
                "safety": "เตียงมีราวกั้นป้องกันการตกเตียง มีอุปกรณ์ป้องกันที่นอนลมสลับลอนเพื่อลดแผลกดทับ",
                "spiritual": "ผู้ป่วยมีหน้าตาหม่นหมอง มีความวิตกกังวลว่าเป็นภาระของครอบครัว",
                "service": "ประสานสิทธิ์ยืมเตียงผู้ป่วยและที่นอนลมจากกองทุนฟื้นฟูฯ ระดับท้องถิ่น",
                "responsible_phase2": "กภ.วิชัย ไตรตรึงษ์",
                "triage": {
                    "physical_score": 3, "physical_desc": "ผู้ป่วยติดเตียง มีแผลกดทับระดับ 2 อัมพาตครึ่งซีกต้องการการฟื้นฟู", "physical_team": ["พยาบาล", "กายภาพ"],
                    "psychological_score": 2, "psychological_desc": "ซึมเศร้าเล็กน้อย รู้สึกเป็นภาระ มีสีหน้ากังวลชัดเจน", "psychological_team": ["พยาบาล"],
                    "social_score": 2, "social_desc": "ผู้ดูแลคนเดียว มีภาระงานภายนอก มีความตึงเครียดด้านเศรษฐกิจ", "social_team": ["พยาบาล", "ชุมชน"],
                    "environment_score": 1, "environment_desc": "บ้านไม้ใต้ถุนสูง มีความชื้นสะสมค่อนข้างมาก", "environment_team": ["ชุมชน"],
                    "nutrition_score": 2, "nutrition_desc": "ได้รับอาหารทางสายยาง น้ำหนักตัวค่อนข้างน้อย ต้องเฝ้าระวังการสำลัก", "nutrition_team": ["นักโภชนาการ"]
                },
                "care_plans": [
                    {
                        "date": "2026-08-25",
                        "problem": "มีแผลกดทับขนาด 2x2 ซม. บริเวณสะโพก",
                        "goal": "แผลแห้งสนิท ขนาดแคบลงและไม่มีการติดเชื้อแทรกซ้อน",
                        "management": "ทำแผลด้วยเทคนิคปลอดเชื้อ พลิกตะแคงตัวทุก 2 ชั่วโมง สอนลูกชายทำแผลและประเมินผิวหนังรอบแผล",
                        "evaluation": "ทำได้"
                    },
                    {
                        "date": "2026-08-25",
                        "problem": "เสี่ยงต่อการเกิดข้อติดแข็งด้านซีกขวาที่มีอาการอ่อนแรง",
                        "goal": "ไม่มีภาวะข้อติดแข็งและคงสภาพมุมการเคลื่อนไหวของข้อต่อไว้ได้",
                        "management": "สอนญาติทำการบริหารข้อต่อ (Passive ROM exercise) แขนและขาขวา วันละ 2 ครั้ง",
                        "evaluation": "ทำไม่ได้"
                    }
                ],
                "responsible_phase3": "พย.สมศรี ไตรตรึงษ์",
                "active_problems": "แผลกดทับสะโพกระดับ 2, ข้อต่อเสี่ยงติดแข็ง, ความเครียดสะสมของผู้ดูแลหลัก",
                "non_active_problems": "ไม่มี",
                "future_plans": [
                    {
                        "date": "2026-09-01",
                        "topic": "ตรวจเช็คขนาดแผลกดทับและทักษะการทำแผลของผู้ดูแล",
                        "goal": "แผลแห้ง ไม่มีหนองหรือขอบแผลแดงอักเสบ",
                        "team_action": "พยาบาลเยี่ยมติดตามแผลและการบริหารข้อต่อ",
                        "evaluation": "รอนัดหมาย"
                    }
                ],
                "doctor_name": "พญ.วิไล ศิริสุข",
                "doctor_note": "ให้ทำแผลทุกวัน ทานยาต้านเกล็ดเลือดสม่ำเสมอ แนะนำสอนลูกชายเรื่องภาวะแทรกซ้อนทางระบบสมองที่ควรมาโรงพยาบาลทันที",
                "nursing_outcome": "ผู้ดูแลสามารถดูแลผู้ป่วยได้",
                "nursing_note": "ผู้ดูแลหลักมีความตระหนักและยินดีทำตามคำแนะนำ แต่มีข้อจำกัดด้านเวลา ควรประสานอสม.ร่วมแวะดูแลเป็นระยะ"
            }
        ]
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(dummy_data, f, ensure_ascii=False, indent=4)
    
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Load current data
patients_db = load_data()

# --- GOOGLE SHEETS & CONFIGURATION INTEGRATION (v4) ---
CONFIG_FILE = "home_visit_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"gsheet_url": "", "gsheet_sync": False}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

config_data = load_config()
if "gsheet_url" not in st.session_state:
    st.session_state["gsheet_url"] = config_data.get("gsheet_url", "")
if "gsheet_sync" not in st.session_state:
    st.session_state["gsheet_sync"] = config_data.get("gsheet_sync", False)

def flatten_patient_for_sheet(p):
    triage = p.get("triage", {})
    
    # Flatten care plans
    care_plans_str = ""
    if p.get("care_plans", []):
        care_plans_str = "; ".join([f"[{cp.get('date')} ปัญหา: {cp.get('problem')} -> เป้าหมาย: {cp.get('goal')} -> กิจกรรม: {cp.get('management')} -> ประเมิน: {cp.get('evaluation')}]" for cp in p["care_plans"]])
        
    # Flatten future plans
    future_plans_str = ""
    if p.get("future_plans", []):
        future_plans_str = "; ".join([f"[{fp.get('date')} ประเด็นติดตาม: {fp.get('topic')} -> เป้าหมาย: {fp.get('goal')} -> กิจกรรมสหวิชาชีพ: {fp.get('team_action')} -> ประเมิน/ลงชื่อ: {fp.get('evaluation')}]" for fp in p["future_plans"]])

    return {
        "HN": p.get("hn", ""),
        "AN": p.get("an", ""),
        "ชื่อ_นามสกุล": p.get("name", ""),
        "เพศ": p.get("gender", ""),
        "อายุ": p.get("age", 0),
        "สถานภาพ": p.get("marriage", ""),
        "ศาสนา": p.get("religion", ""),
        "รพ_สต": p.get("pcsu", ""),
        "การวินิจฉัย": p.get("diagnosis", ""),
        "ประเภทผู้ป่วย": p.get("patient_type", ""),
        "ADL_คะแนน": p.get("adl", 0),
        "อาชีพ": p.get("occupation", ""),
        "รายได้_บาท_เดือน": p.get("income", ""),
        "สิทธิ์รักษา": p.get("benefit", ""),
        "ที่อยู่": p.get("address", ""),
        "เบอร์โทร": p.get("phone", ""),
        "ผู้ดูแลหลัก": p.get("caregiver", ""),
        "โรคประจำตัว": p.get("underlying", ""),
        "ประวัติแพ้ยา": p.get("drug_allergy", ""),
        "ประวัติแพ้อาหาร": p.get("food_allergy", ""),
        "วัตถุประสงค์การเยี่ยม": ", ".join(p.get("objectives", [])),
        "ทีมวิชาชีพ": ", ".join(p.get("planning_team", [])),
        "เครื่องมืออุปกรณ์": ", ".join(p.get("equipment", [])),
        "ผู้รับผิดชอบ_Phase1_ROPE": p.get("responsible_phase1", ""),
        "ผังครอบครัว": p.get("genogram", ""),
        "วันที่เยี่ยม": p.get("visit_date", ""),
        "เวลาเริ่ม": p.get("start_time", ""),
        "เวลาสิ้นสุด": p.get("end_time", ""),
        "ระยะเวลาเยี่ยม_นาที": p.get("duration", 0),
        "Immobility": p.get("immobility", ""),
        "Nutrition": p.get("nutrition", ""),
        "Housing": p.get("housing", ""),
        "Other_People": p.get("other_people", ""),
        "Medication": p.get("medication", ""),
        "Examination": p.get("examination", ""),
        "Safety": p.get("safety", ""),
        "Spiritual": p.get("spiritual", ""),
        "Service": p.get("service", ""),
        "ผู้รับผิดชอบ_Phase2_GTIME": p.get("responsible_phase2", ""),
        "คะแนน_ร่างกาย_Physical": triage.get("physical_score", 0),
        "รายละเอียด_ร่างกาย": triage.get("physical_desc", ""),
        "คะแนน_จิตใจ_Psychological": triage.get("psychological_score", 0),
        "รายละเอียด_จิตใจ": triage.get("psychological_desc", ""),
        "คะแนน_สังคม_Social": triage.get("social_score", 0),
        "รายละเอียด_สังคม": triage.get("social_desc", ""),
        "คะแนน_สิ่งแวดล้อม_Environment": triage.get("environment_score", 0),
        "รายละเอียด_สิ่งแวดล้อม": triage.get("environment_desc", ""),
        "คะแนน_โภชนาการ_Nutrition": triage.get("nutrition_score", 0),
        "รายละเอียด_โภชนาการ": triage.get("nutrition_desc", ""),
        "แผนการพยาบาล": care_plans_str,
        "Active_Problems": p.get("active_problems", ""),
        "Non_Active_Problems": p.get("non_active_problems", ""),
        "แผนติดตามอนาคต": future_plans_str,
        "ชื่อแพทย์": p.get("doctor_name", ""),
        "บันทึกแพทย์": p.get("doctor_note", ""),
        "ผลลัพธ์พยาบาล": p.get("nursing_outcome", ""),
        "บันทึกพยาบาล": p.get("nursing_note", ""),
        "ผู้รับผิดชอบ_Phase3_CPR": p.get("responsible_phase3", ""),
        "วันที่อัปเดตเข้าระบบ": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def send_to_google_sheets(payload, url=None):
    if not url:
        url = st.session_state.get("gsheet_url", "")
    if not url:
        return False, "ไม่ได้ตั้งค่า Google Sheets Web App URL"
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("status") == "success":
                return True, "ซิงค์ข้อมูลลง Google Sheets สำเร็จ!"
            else:
                return False, f"ข้อผิดพลาดจาก Apps Script: {res_json.get('message', 'ไม่ระบุ')}"
        else:
            return False, f"HTTP Error {response.status_code} - กรุณาตรวจสอบสถานะเว็บแอป"
    except Exception as e:
        return False, f"ไม่สามารถเชื่อมต่อ Google Sheets ได้: {str(e)}"

# --- LOGIN SECURITY ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "user_role" not in st.session_state:
    st.session_state["user_role"] = ""

PRESET_USERS = {
    "admin": {"password": "kppadmin", "role": "admin", "name": "ผู้ดูแลระบบ (Admin)"},
    "staff": {"password": "kppstaff", "role": "staff", "name": "เจ้าหน้าที่สหวิชาชีพ (Staff)"},
    "visitor": {"password": "kppvisitor", "role": "visitor", "name": "ผู้เข้าเยี่ยมชม (Visitor)"}
}

if not st.session_state["logged_in"]:
    # Elegant Centered Login Screen with Kamphaeng Phet theme
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("""
        <div style="background-color: #F8FAFC; border: 2px solid #E2E8F0; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            <h2 style="text-align: center; color: #1E3A8A; margin-bottom: 5px;">🔑 เข้าสู่ระบบเยี่ยมบ้าน v3</h2>
            <p style="text-align: center; color: #475569; font-size: 14px; margin-bottom: 25px;">
                ระบบบันทึกและประเมินผลการเยี่ยมบ้านสหวิชาชีพ จังหวัดกำแพงเพชร
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            login_username = st.text_input("👤 ชื่อผู้ใช้งาน (Username)", placeholder="ระบุชื่อผู้ใช้ (admin / staff / visitor)")
            login_password = st.text_input("🔒 รหัสผ่าน (Password)", type="password", placeholder="ระบุรหัสผ่าน")
            submit_login = st.form_submit_button("🔓 ลงชื่อเข้าใช้")
            
            if submit_login:
                if login_username in PRESET_USERS and PRESET_USERS[login_username]["password"] == login_password:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = login_username
                    st.session_state["user_role"] = PRESET_USERS[login_username]["role"]
                    st.success(f"ยินดีต้อนรับคุณ {PRESET_USERS[login_username]['name']} เข้าสู่ระบบสำเร็จ!")
                    st.rerun()
                else:
                    st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
                    
        st.markdown("""
        <div style="margin-top: 20px; padding: 15px; background-color: #EFF6FF; border-radius: 8px; border: 1px solid #BFDBFE; font-size: 13px; color: #1E40AF;">
            <b>ℹ️ บัญชีผู้ใช้งานเริ่มต้นสำหรับสาธิต:</b><br>
            • <b>ผู้ดูแลระบบ (Admin)</b>: Username: <code>admin</code> / Password: <code>kppadmin</code> (จัดการและลบได้ทุกส่วน)<br>
            • <b>ผู้ใช้งานทั่วไป (Staff)</b>: Username: <code>staff</code> / Password: <code>kppstaff</code> (บันทึก/แก้ไข/ซิงค์ชีตปกติ)<br>
            • <b>ผู้เยี่ยมชม (Visitor)</b>: Username: <code>visitor</code> / Password: <code>kppvisitor</code> (ดูข้อมูลย้อนหลังและแดชบอร์ดอย่างเดียว)
        </div>
        """, unsafe_allow_html=True)
else:
    
    # Helper function to compute urgency score level
    def get_urgency_level(triage):
        scores = [
            triage.get("physical_score", 0),
            triage.get("psychological_score", 0),
            triage.get("social_score", 0),
            triage.get("environment_score", 0),
            triage.get("nutrition_score", 0)
        ]
        max_score = max(scores)
        if max_score >= 3:
            return "ความเร่งด่วนสูง (High)"
        elif max_score == 2:
            return "ความเร่งด่วนปานกลาง"
        else:
            return "ปกติ / ความเร่งด่วนต่ำ"
    
    # Sidebar Navigation
    st.sidebar.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🏠 ระบบเยี่ยมบ้าน v2</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='text-align: center; font-size: 14px;'>แนวคิด <b>ROPE</b> & <b>G-TIME</b> & <b>CPR</b><br><b>จ.กำแพงเพชร</b></p>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio(
        "เลือกหน้าการทำงาน",
        ["📊 แดชบอร์ดวิเคราะห์ภาพรวม", "📋 ทะเบียนเคสและประวัติ", "➕ บันทึกเคสเยี่ยมบ้านใหม่", "ℹ️ ข้อมูลระบบเยี่ยมบ้าน"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "💡 **คำแนะนำวิธีรันโลคอล**:\n"
        "1. ติดตั้ง Streamlit: `pip install streamlit plotly pandas`\n"
        "2. รันคำสั่ง: `streamlit run home_visit_app_v2.py`"
    )
    
    # ----------------- PAGE 1: DASHBOARD -----------------
    if menu == "📊 แดชบอร์ดวิเคราะห์ภาพรวม":
        st.markdown("<h1 style='color: #1E3A8A;'>📈 แดชบอร์ดสรุปวิเคราะห์ข้อมูลภาพรวม (Analytics Dashboard)</h1>", unsafe_allow_html=True)
        st.markdown("ข้อมูลสถิติด้านการลงพื้นที่และระดับความเสี่ยงของผู้ป่วยทั้งหมด เพื่อการจัดการเยี่ยมบ้านอย่างมีประสิทธิภาพ")
        st.write("")
    
        if len(patients_db) == 0:
            st.warning("ยังไม่มีข้อมูลผู้ป่วยในระบบ กรุณาเพิ่มเคสใหม่ก่อนเริ่มต้น")
        else:
            # Calculate statistics
            total_cases = len(patients_db)
            high_risk = 0
            med_risk = 0
            low_risk = 0
            
            objectives_count = {}
            team_count = {}
            patient_type_count = {}
            underlying_count = {}
            pcsu_count = {}
            
            adl_groups = {"ติดเตียง (ADL 0-4)": 0, "ติดบ้าน (ADL 5-11)": 0, "ติดสังคม (ADL 12-20)": 0}
            care_plan_eval = {"ทำได้": 0, "ทำไม่ได้": 0}
            total_durations = 0
            valid_duration_count = 0
    
            outcome_count = {
                "ผู้ป่วยสามารถที่จะดูแลตนเองได้": 0,
                "ผู้ดูแลสามารถดูแลผู้ป่วยได้": 0,
                "ลดภาวะแทรกซ้อน": 0,
                "ลดอัตราพิการ/เสียชีวิต": 0,
                "อื่นๆ": 0
            }
            
            avg_scores = {
                "ร่างกาย (Physical)": 0,
                "จิตใจ (Psychological)": 0,
                "สังคม/ผู้ดูแล (Social)": 0,
                "สิ่งแวดล้อม (Environment)": 0,
                "โภชนาการ (Nutrition)": 0
            }
    
            for p in patients_db:
                # Urgency level classification
                lvl = get_urgency_level(p["triage"])
                if lvl == "ความเร่งด่วนสูง (High)":
                    high_risk += 1
                elif lvl == "ความเร่งด่วนปานกลาง":
                    med_risk += 1
                else:
                    low_risk += 1
                    
                # ADL categorization
                adl_val = p.get("adl", 20)
                if adl_val <= 4:
                    adl_groups["ติดเตียง (ADL 0-4)"] += 1
                elif adl_val <= 11:
                    adl_groups["ติดบ้าน (ADL 5-11)"] += 1
                else:
                    adl_groups["ติดสังคม (ADL 12-20)"] += 1
    
                # Patient Type frequency
                ptype = p.get("patient_type", "อื่นๆ")
                patient_type_count[ptype] = patient_type_count.get(ptype, 0) + 1
    
                # Underlying disease frequency
                underlyings_raw = p.get("underlying", "")
                if underlyings_raw:
                    for disease in [d.strip() for d in underlyings_raw.split(",") if d.strip()]:
                        underlying_count[disease] = underlying_count.get(disease, 0) + 1
    
                # PCSU (รพ.สต.) frequency
                pc_val = p.get("pcsu", "อื่นๆ")
                pcsu_count[pc_val] = pcsu_count.get(pc_val, 0) + 1
    
                # Visit duration
                if "duration" in p:
                    total_durations += p["duration"]
                    valid_duration_count += 1
    
                # Care Plan Evaluations
                for cp in p.get("care_plans", []):
                    ev = cp.get("evaluation", "ทำได้")
                    if "ทำได้" in ev and "ทำไม่ได้" not in ev:
                        care_plan_eval["ทำได้"] += 1
                    elif "ทำไม่ได้" in ev:
                        care_plan_eval["ทำไม่ได้"] += 1
    
                # Objectives frequency
                for obj in p.get("objectives", []):
                    objectives_count[obj] = objectives_count.get(obj, 0) + 1
                    
                # Team frequency
                for team in p.get("planning_team", []):
                    team_count[team] = team_count.get(team, 0) + 1
                    
                # Nursing Outcomes
                outcome = p.get("nursing_outcome", "อื่นๆ")
                if outcome in outcome_count:
                    outcome_count[outcome] += 1
                else:
                    outcome_count["อื่นๆ"] += 1
                    
                # Average scores
                avg_scores["ร่างกาย (Physical)"] += p["triage"].get("physical_score", 0)
                avg_scores["จิตใจ (Psychological)"] += p["triage"].get("psychological_score", 0)
                avg_scores["สังคม/ผู้ดูแล (Social)"] += p["triage"].get("social_score", 0)
                avg_scores["สิ่งแวดล้อม (Environment)"] += p["triage"].get("environment_score", 0)
                avg_scores["โภชนาการ (Nutrition)"] += p["triage"].get("nutrition_score", 0)
    
            # Normalize average scores
            for k in avg_scores:
                avg_scores[k] = round(avg_scores[k] / total_cases, 2)
    
            # Average visit duration calculation
            avg_dur = round(total_durations / valid_duration_count, 1) if valid_duration_count > 0 else 0
    
            # Dashboard KPI Cards
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("เคสเยี่ยมบ้านทั้งหมด", f"{total_cases} เคส", help="จำนวนผู้ป่วยที่ได้รับการประเมินและขึ้นทะเบียน")
            with col2:
                st.metric("🔴 ความเร่งด่วนสูง (High)", f"{high_risk} เคส", delta=f"{round(high_risk/total_cases*100,1)}%", delta_color="inverse")
            with col3:
                st.metric("🟡 ความเร่งด่วนปานกลาง", f"{med_risk} เคส", delta=f"{round(med_risk/total_cases*100,1)}%", delta_color="off")
            with col4:
                st.metric("🟢 ปกติ / ความเร่งด่วนต่ำ", f"{low_risk} เคส", delta=f"{round(low_risk/total_cases*100,1)}%", delta_color="normal")
            with col5:
                st.metric("⏱️ เวลาเยี่ยมบ้านเฉลี่ย", f"{avg_dur} นาที", help="ระยะเวลาเฉลี่ยในการเยี่ยมคนไข้ต่อครั้ง")
    
            st.markdown("---")
    
            # Visualizations row 1
            vcol1, vcol2 = st.columns(2)
            with vcol1:
                st.markdown("#### 👤 สถิติสัดส่วนตามประเภทผู้ป่วย (Patient Type Distribution)")
                if patient_type_count:
                    df_ptype = pd.DataFrame(list(patient_type_count.items()), columns=["ประเภทผู้ป่วย", "จำนวนเคส"])
                    fig_ptype = px.pie(df_ptype, values="จำนวนเคส", names="ประเภทผู้ป่วย", hole=0.4,
                                       color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_ptype.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300)
                    st.plotly_chart(fig_ptype, use_container_width=True)
                else:
                    st.info("ไม่มีข้อมูลประเภทผู้ป่วย")
    
            with vcol2:
                st.markdown("#### 🏥 จำนวนผู้ป่วยแยกตาม รพ.สต. ในสังกัด (Kamphaeng Phet PCSU)")
                if pcsu_count:
                    df_pcsu = pd.DataFrame(list(pcsu_count.items()), columns=["รพ.สต.", "จำนวนคนไข้"]).sort_values(by="จำนวนคนไข้", ascending=True)
                    fig_pcsu = px.bar(df_pcsu, y="รพ.สต.", x="จำนวนคนไข้", orientation='h',
                                      color="รพ.สต.", color_discrete_sequence=px.colors.qualitative.Safe)
                    fig_pcsu.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=300)
                    st.plotly_chart(fig_pcsu, use_container_width=True)
                else:
                    st.info("ไม่มีข้อมูล รพ.สต.")
    
            st.markdown("---")
    
            # Visualizations row 2 (Underlying and ADL)
            vcol1_2, vcol2_2 = st.columns(2)
            with vcol1_2:
                st.markdown("#### 🩺 สถิติโรคประจำตัวที่พบมากที่สุด (Underlying Diseases)")
                if underlying_count:
                    df_und = pd.DataFrame(list(underlying_count.items()), columns=["โรคประจำตัว", "จำนวนเคส"]).sort_values(by="จำนวนเคส", ascending=False)
                    fig_und = px.bar(df_und, x="โรคประจำตัว", y="จำนวนเคส", color="โรคประจำตัว", color_discrete_sequence=px.colors.qualitative.Prism)
                    fig_und.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=300)
                    st.plotly_chart(fig_und, use_container_width=True)
                else:
                    st.info("ไม่มีข้อมูลโรคประจำตัว")
    
            with vcol2_2:
                st.markdown("#### 📈 สัดส่วนความพึ่งพาแยกตามเกณฑ์ ADL (ADL Grouping)")
                df_adl = pd.DataFrame(list(adl_groups.items()), columns=["กลุ่มความพึ่งพา", "จำนวนคน"])
                fig_adl = px.bar(df_adl, x="กลุ่มความพึ่งพา", y="จำนวนคน", color="กลุ่มความพึ่งพา", color_discrete_sequence=["#EF4444", "#F59E0B", "#10B981"])
                fig_adl.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=300)
                st.plotly_chart(fig_adl, use_container_width=True)
    
            st.markdown("---")
    
            # Visualizations row 3 (Radar & CPR)
            vcol3, vcol4 = st.columns(2)
            with vcol3:
                st.markdown("#### 🕸️ ระดับความเสี่ยงเฉลี่ย 5 ด้าน (Average Triage Radar)")
                categories = list(avg_scores.keys())
                values = list(avg_scores.values())
                
                # Close the polygon for radar chart
                categories += [categories[0]]
                values += [values[0]]
                
                fig_radar = go.Figure(data=go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    fillcolor='rgba(30, 58, 138, 0.2)',
                    line=dict(color='#1E3A8A', width=2),
                    name='ระดับความเสี่ยงเฉลี่ย'
                ))
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 3],
                            tickvals=[0, 1, 2, 3],
                            ticktext=['0 (ปกติ)', '1 (ต่ำ)', '2 (กลาง)', '3 (สูง/วิกฤต)']
                        )
                    ),
                    showlegend=False,
                    margin=dict(t=20, b=20, l=40, r=40),
                    height=320
                )
                st.plotly_chart(fig_radar, use_container_width=True)
    
            with vcol4:
                st.markdown("#### 📊 ผลสัมฤทธิ์การประเมินกิจกรรมพยาบาล (Nursing Care Plan Capability)")
                df_eval = pd.DataFrame(list(care_plan_eval.items()), columns=["ผลการประเมิน", "จำนวนกิจกรรม"])
                fig_eval = px.pie(df_eval, values="จำนวนกิจกรรม", names="ผลการประเมิน", hole=0.4,
                                  color="ผลการประเมิน", color_discrete_map={"ทำได้": "#10B981", "ทำไม่ได้": "#EF4444"})
                fig_eval.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320)
                st.plotly_chart(fig_eval, use_container_width=True)
    
    # ----------------- PAGE 2: PATIENT REGISTRY -----------------
    elif menu == "📋 ทะเบียนเคสและประวัติ":
        st.markdown("<h1 style='color: #1E3A8A;'>📋 ทะเบียนคนไข้และประวัติการเยี่ยมบ้าน</h1>", unsafe_allow_html=True)
        st.markdown("สืบค้นข้อมูลประวัติการบันทึก ทบทวนเคสเดิม และปรับปรุงรายงานการเยี่ยมบ้าน")
        st.write("")
    
        if len(patients_db) == 0:
            st.info("ไม่มีข้อมูลผู้ป่วยในระบบ")
        else:
            # Search & Filter area
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                search_query = st.text_input("🔍 ค้นหาผู้ป่วยด้วย ชื่อ-นามสกุล, HN, โรคประจำตัว, หรืออาการวินิจฉัย:", "")
            with col2:
                triage_filter = st.selectbox(
                    "🚦 กรองตามความเร่งด่วน:",
                    ["ทั้งหมด", "ความเร่งด่วนสูง (High)", "ความเร่งด่วนปานกลาง", "ปกติ / ความเร่งด่วนต่ำ"]
                )
            with col3:
                ptype_filter = st.selectbox(
                    "👤 กรองตามประเภทผู้ป่วย:",
                    ["ทั้งหมด", "stroke", "cancer", "ติดเตียง", "ดูแลหลังผ่าตัด", "มารดาหลังคลอด", "จิตเวช", "DM", "HT", "พิการ", "อื่นๆ"]
                )
    
            # Filter processing
            filtered_patients = []
            for p in patients_db:
                # Urgency filter match
                lvl = get_urgency_level(p["triage"])
                if triage_filter != "ทั้งหมด" and lvl != triage_filter:
                    continue
                
                # Patient Type filter match
                if ptype_filter != "ทั้งหมด" and p.get("patient_type", "อื่นๆ") != ptype_filter:
                    continue
                    
                # Search filter match
                query = search_query.lower()
                if query:
                    text_pool = f"{p['name']} {p['hn']} {p.get('an','')} {p.get('underlying','')} {p.get('diagnosis','')}".lower()
                    if query not in text_pool:
                        continue
                filtered_patients.append(p)
    
            st.markdown(f"**พบคนไข้ตรงตามเงื่อนไข: {len(filtered_patients)} ราย** จากทั้งหมด {len(patients_db)} ราย")
    
            if len(filtered_patients) > 0:
                # Create interactive table listing patients
                table_rows = []
                for idx, p in enumerate(filtered_patients):
                    lvl = get_urgency_level(p["triage"])
                    badge = "🔴 สูง" if "สูง" in lvl else ("🟡 กลาง" if "ปานกลาง" in lvl else "🟢 ต่ำ")
                    table_rows.append({
                        "ลำดับ": idx + 1,
                        "HN": p["hn"],
                        "ชื่อ-นามสกุล": p["name"],
                        "ประเภทผู้ป่วย": p.get("patient_type", "อื่นๆ"),
                        "การวินิจฉัย (Diagnosis)": p.get("diagnosis", "-"),
                        "ความเร่งด่วน": badge,
                        "ADL (Barthel)": f"{p['adl']} คะแนน",
                        "ผู้ดูแลหลัก": p.get("caregiver", "-"),
                        "รพ.สต.": p.get("pcsu", "-")
                    })
                
                df_table = pd.DataFrame(table_rows)
                st.dataframe(df_table, use_container_width=True, hide_index=True)
    
                st.write("")
                st.markdown("### 🔎 เลือกผู้ป่วยเพื่อดูรายละเอียดแบบฟอร์ม ROPE / G-TIME / CPR")
                selected_hn = st.selectbox(
                    "ระบุ HN เพื่อดึงแฟ้มข้อมูลสุขภาพ:",
                    options=[p["hn"] for p in filtered_patients],
                    format_func=lambda hn: f"{hn} - {next(p['name'] for p in filtered_patients if p['hn'] == hn)}"
                )
    
                # Get the selected patient details
                patient = next(p for p in filtered_patients if p["hn"] == selected_hn)
    
                # Show details in organized tabs
    
                # ---- PRINT SUMMARY AND DOWNLOAD REPORT ----
                col_p1, col_p2 = st.columns([2, 1])
                with col_p1:
                    show_print_view = st.checkbox("🖨️ เปิดโหมดมุมมองสำหรับพิมพ์รายงาน (Print-Friendly View)")
                with col_p2:
                    # Compile dynamic TXT report for download
                    summary_text = f"""==================================================
    รายงานสรุปการเยี่ยมบ้านและการดูแลพยาบาล จังหวัดกำแพงเพชร
    ==================================================
    เลขที่ HN: {patient['hn']}  เลขที่ AN: {patient.get('an', '-')}
    ชื่อ-นามสกุล: {patient['name']}  เพศ: {patient['gender']}  อายุ: {patient['age']} ปี
    ประเภทผู้ป่วย: {patient.get('patient_type', '-')}
    โรคประจำตัว: {patient.get('underlying', '-')}
    การวินิจฉัยโรค (Diagnosis): {patient.get('diagnosis', '-')}
    คะแนน ADL: {patient.get('adl', '-')} คะแนน (ความเร่งด่วน: {get_urgency_level(patient['triage'])})
    ผู้ดูแลหลัก: {patient.get('caregiver', '-')}
    เบอร์ติดต่อ: {patient.get('phone', '-')}
    สิทธิการรักษา: {patient.get('benefit', '-')}
    เขต รพ.สต. จังหวัดกำแพงเพชร: {patient.get('pcsu', '-')}
    ที่อยู่สำหรับเยี่ยมบ้าน: {patient.get('address', '-')}
    
    PHASE 1: PRE-HOME VISIT (ROPE)
    ------------------------------
    - วัตถุประสงค์การเยี่ยม (Objectives): {", ".join(patient.get("objectives", []))}
    - ทีมวิชาชีพวางแผน (Planning Team): {", ".join(patient.get("planning_team", []))}
    - อุปกรณ์เตรียมเยี่ยม (Equipment): {", ".join(patient.get("equipment", []))}
    - ผู้รับผิดชอบจัดเตรียมประวัติและแผน (Phase 1): {patient.get('responsible_phase1', '-')}
    
    PHASE 2: HOME VISIT (G-TIME & INHOMESSS)
    ----------------------------------------
    - วันที่เยี่ยมบ้าน: {patient.get('visit_date', '-')} เวลา: {patient.get('start_time', '')} - {patient.get('end_time', '')} (รวม {patient.get('duration', 0)} นาที)
    - ผังครอบครัวและสัมพันธภาพ: {patient.get('genogram', '-')}
    - การประเมิน INHOMESSS 9 ด้าน:
      1. Immobility: {patient.get('immobility', '-')}
      2. Nutrition: {patient.get('nutrition', '-')}
      3. Housing: {patient.get('housing', '-')}
      4. Other People: {patient.get('other_people', '-')}
      5. Medication: {patient.get('medication', '-')}
      6. Examination: {patient.get('examination', '-')}
      7. Safety: {patient.get('safety', '-')}
      8. Spiritual Health: {patient.get('spiritual', '-')}
      9. Service: {patient.get('service', '-')}
    - ผู้ลงพื้นที่ประเมินสุขภาพ (Phase 2): {patient.get('responsible_phase2', '-')}
    
    ระดับความเร่งด่วนรายด้าน (Urgency Triage Scoring):
      - ร่างกาย (Physical): {patient.get('triage', {}).get('physical_score', 0)} ({patient.get('triage', {}).get('physical_desc', '')})
      - จิตใจ (Psychological): {patient.get('triage', {}).get('psychological_score', 0)} ({patient.get('triage', {}).get('psychological_desc', '')})
      - สังคม/ผู้ดูแล (Social): {patient.get('triage', {}).get('social_score', 0)} ({patient.get('triage', {}).get('social_desc', '')})
      - สิ่งแวดล้อม (Environment): {patient.get('triage', {}).get('environment_score', 0)} ({patient.get('triage', {}).get('environment_desc', '')})
      - โภชนาการ (Nutrition): {patient.get('triage', {}).get('nutrition_score', 0)} ({patient.get('triage', {}).get('nutrition_desc', '')})
    
    PHASE 3: POST-HOME VISIT (CPR)
    ------------------------------
    - Active Problems (ปัญหาที่กำลังแก้ไข/ต้องประเมินต่อ): {patient.get('active_problems', '-')}
    - Non-active Problems (ปัญหาที่แก้ไขสำเร็จแล้ว): {patient.get('non_active_problems', '-')}
    - แผนติดตามระยะถัดไป (Future Planning):
    """
                    if patient.get("future_plans", []):
                        for fp in patient["future_plans"]:
                            summary_text += f"  • [{fp.get('date', '')}] หัวข้อ: {fp.get('topic', '')} | เป้าหมาย: {fp.get('goal', '')} | กิจกรรม: {fp.get('team_action', '')}\n"
                    else:
                        summary_text += "  • ไม่มีแผนระบุ\n"
    
                    summary_text += f"""
    บันทึกสรุปสุดท้าย (Recording):
    - บันทึกแพทย์ (Doctor's Note): {patient.get('doctor_note', 'ไม่มีบันทึก')} (โดย {patient.get('doctor_name', '-')})
    - ประเมินพยาบาลหลัก (Nursing Note): {patient.get('nursing_note', 'ไม่มีบันทึก')} (ผลลัพธ์: {patient.get('nursing_outcome', '-')})
    - ผู้สรุปรายงานและนัดหมาย (Phase 3): {patient.get('responsible_phase3', '-')}
    """
                    st.download_button(
                        label="📥 ดาวน์โหลดไฟล์สรุปรายงาน (.txt)",
                        data=summary_text,
                        file_name=f"Home_Visit_Summary_{patient['hn']}.txt",
                        mime="text/plain"
                    )
    
                st.write("")
    
                # Render logic based on print mode
                if show_print_view:
                    st.markdown("<hr style='border: 2px solid #1E3A8A;'>", unsafe_allow_html=True)
                    st.markdown("<h2 style='text-align: center; color: #1E3A8A; margin-bottom: 5px;'>🏥 รายงานสรุปผลการเยี่ยมบ้านและการดูแลพยาบาล</h2>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align: center; font-size: 14px;'>รพ.สต. ในสังกัดสำนักงานสาธารณสุขจังหวัดกำแพงเพชร • ระบบเยี่ยมบ้านสหวิชาชีพ (ROPE & G-TIME & CPR)</p>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # HTML and Inline CSS for High-Quality Printable Sheet
                    st.markdown("""
                    <style>
                    @media print {
                        body { color: black; background: white; }
                        .no-print { display: none !important; }
                        .print-box { border: 1px solid #ccc !important; box-shadow: none !important; page-break-inside: avoid; }
                    }
                    .print-box { 
                        border: 1px solid #1E3A8A; 
                        background-color: #FAFAFA; 
                        padding: 20px; 
                        border-radius: 8px; 
                        margin-bottom: 20px; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    }
                    .print-header { 
                        color: #1E3A8A; 
                        font-size: 16px;
                        font-weight: bold; 
                        border-bottom: 2px solid #1E3A8A; 
                        padding-bottom: 5px; 
                        margin-bottom: 15px; 
                    }
                    </style>
                    """, unsafe_allow_html=True)
    
                    # SECTION 1: Patient Demographics Card (Phase 1)
                    st.markdown(f"""
                    <div class="print-box">
                        <div class="print-header">📋 ข้อมูลประวัติและผู้ดูแล (PHASE 1: Review History - ROPE)</div>
                        <table style="width:100%; border-collapse: collapse; font-size: 14px;">
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="width: 25%; font-weight: bold; padding: 8px 0;">ชื่อ-นามสกุล:</td><td style="width: 25%; padding: 8px 0;">{patient['name']}</td>
                                <td style="width: 25%; font-weight: bold; padding: 8px 0;">เลขที่ HN:</td><td style="width: 25%; padding: 8px 0;">{patient['hn']}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="font-weight: bold; padding: 8px 0;">เลขที่ AN:</td><td style="padding: 8px 0;">{patient.get('an', '-')}</td>
                                <td style="font-weight: bold; padding: 8px 0;">เพศ / อายุ:</td><td style="padding: 8px 0;">{patient['gender']} / {patient['age']} ปี</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="font-weight: bold; padding: 8px 0;">การวินิจฉัยโรค (Diagnosis):</td><td style="padding: 8px 0; color: #1E3A8A; font-weight: bold;">{patient.get('diagnosis', '-')}</td>
                                <td style="font-weight: bold; padding: 8px 0;">ประเภทผู้ป่วย:</td><td style="padding: 8px 0; color: #D97706; font-weight: bold;">{patient.get('patient_type', '-')}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="font-weight: bold; padding: 8px 0;">โรคประจำตัว (Underlying):</td><td style="padding: 8px 0;">{patient.get('underlying', '-')}</td>
                                <td style="font-weight: bold; padding: 8px 0;">คะแนน ADL (Barthel Index):</td><td style="padding: 8px 0; font-weight: bold;">{patient.get('adl', '-')} คะแนน</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="font-weight: bold; padding: 8px 0;">ผู้ดูแลหลัก (Caregiver):</td><td style="padding: 8px 0;">{patient.get('caregiver', '-')}</td>
                                <td style="font-weight: bold; padding: 8px 0;">เบอร์โทรศัพท์:</td><td style="padding: 8px 0;">{patient.get('phone', '-')}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="font-weight: bold; padding: 8px 0;">สิทธิการรักษา:</td><td style="padding: 8px 0;">{patient.get('benefit', '-')}</td>
                                <td style="font-weight: bold; padding: 8px 0;">รพ.สต. รับผิดชอบ:</td><td style="padding: 8px 0;">{patient.get('pcsu', '-')}</td>
                            </tr>
                            <tr>
                                <td style="font-weight: bold; padding: 8px 0;">ที่อยู่สำหรับเยี่ยมบ้าน:</td><td colspan="3" style="padding: 8px 0;">{patient.get('address', '-')}</td>
                            </tr>
                        </table>
                        <div style="margin-top: 15px; text-align: right; font-size: 13px; color: gray;">
                            <b>ผู้รับผิดชอบจัดเตรียมประวัติและแผน (Phase 1):</b> {patient.get('responsible_phase1', 'ไม่ได้ระบุ')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
                    # Objectives, Planning, Equipment
                    st.markdown(f"""
                    <div class="print-box">
                        <div class="print-header">🎯 วัตถุประสงค์ แผน และความพร้อมในการพรีเยี่ยม (Objectives & Planning & Equipment)</div>
                        <table style="width:100%; border-collapse: collapse; font-size: 14px;">
                            <tr>
                                <td style="width:33%; vertical-align: top; padding: 8px;">
                                    <div style="font-weight: bold; color: #1E3A8A; margin-bottom: 5px;">🎯 วัตถุประสงค์การเยี่ยม (O)</div>
                                    {"<br>".join([f"- {o}" for o in patient.get("objectives", [])])}
                                </td>
                                <td style="width:33%; vertical-align: top; padding: 8px;">
                                    <div style="font-weight: bold; color: #1E3A8A; margin-bottom: 5px;">🩺 ทีมวิชาชีพวางแผนร่วม (P)</div>
                                    {"<br>".join([f"- {t}" for t in patient.get("planning_team", [])])}
                                </td>
                                <td style="width:33%; vertical-align: top; padding: 8px;">
                                    <div style="font-weight: bold; color: #1E3A8A; margin-bottom: 5px;">📦 เครื่องมือและอุปกรณ์ (E)</div>
                                    {"<br>".join([f"- {e}" for e in patient.get("equipment", [])])}
                                </td>
                            </tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
    
                    # SECTION 2: G-TIME and INHOMESSS
                    st.markdown(f"""
                    <div class="print-box">
                        <div class="print-header">🏡 ผลการประเมินสภาวะแวดล้อมที่บ้าน (PHASE 2: G-TIME & INHOMESSS)</div>
                        <div style="margin-bottom: 12px; font-size: 14px;">
                            <b>ผังครอบครัว บริบทสัมพันธภาพ:</b> {patient.get('genogram', '-')}
                        </div>
                        <div style="margin-bottom: 15px; font-size: 14px; background-color: #EBF5FF; padding: 10px; border-radius: 4px; border-left: 4px solid #1E3A8A;">
                            <b>วันที่ลงเยี่ยมบ้าน:</b> {patient.get('visit_date', '-')} &nbsp;&nbsp;|&nbsp;&nbsp; 
                            <b>รวมระยะเวลาเยี่ยม:</b> {patient.get('duration', 0)} นาที ({patient.get('start_time', '')} - {patient.get('end_time', '')})
                        </div>
                        <div style="font-weight: bold; color: #1E3A8A; margin-bottom: 10px; font-size: 14px;">ผลการประเมินสภาพแวดล้อมและบริบทเยี่ยมบ้าน 9 มิติ (INHOMESSS):</div>
                        <table style="width:100%; border-collapse: collapse; font-size: 13px; margin-bottom: 10px;" border="1" cellpadding="8" cellspacing="0" bordercolor="#ddd">
                            <tr style="background-color: #F3F4F6; font-weight: bold;">
                                <td style="width: 33%;">มิติการเคลื่อนไหวและการกิน</td>
                                <td style="width: 33%;">มิติที่อยู่อาศัยและการกินยา</td>
                                <td style="width: 33%;">มิติความปลอดภัยและระบบความช่วยเหลือ</td>
                            </tr>
                            <tr>
                                <td style="vertical-align: top;">
                                    <b>1. Immobility (การขยับเคลื่อนไหว):</b><br>{patient.get('immobility', '-')}
                                </td>
                                <td style="vertical-align: top;">
                                    <b>4. Other People (ผู้ดูแล/สัมพันธภาพ):</b><br>{patient.get('other_people', '-')}
                                </td>
                                <td style="vertical-align: top;">
                                    <b>7. Safety (ความปลอดภัยที่บ้าน):</b><br>{patient.get('safety', '-')}
                                </td>
                            </tr>
                            <tr>
                                <td style="vertical-align: top;">
                                    <b>2. Nutrition (โภชนาการและการทาน):</b><br>{patient.get('nutrition', '-')}
                                </td>
                                <td style="vertical-align: top;">
                                    <b>5. Medication (พฤติกรรมใช้ยา):</b><br>{patient.get('medication', '-')}
                                </td>
                                <td style="vertical-align: top;">
                                    <b>8. Spiritual Health (จิตวิญญาณ/ความเชื่อ):</b><br>{patient.get('spiritual', '-')}
                                </td>
                            </tr>
                            <tr>
                                <td style="vertical-align: top;">
                                    <b>3. Housing (โครงสร้างความสะดวก):</b><br>{patient.get('housing', '-')}
                                </td>
                                <td style="vertical-align: top;">
                                    <b>6. Examination (การตรวจสัญญาณชีพ):</b><br>{patient.get('examination', '-')}
                                </td>
                                <td style="vertical-align: top;">
                                    <b>9. Service (การเข้าถึงสิทธิ์ช่วยเหลือ):</b><br>{patient.get('service', '-')}
                                </td>
                            </tr>
                        </table>
                        <div style="margin-top: 15px; text-align: right; font-size: 13px; color: gray;">
                            <b>ผู้ลงพื้นที่ตรวจคัดกรองและประเมิน (Phase 2):</b> {patient.get('responsible_phase2', 'ไม่ได้ระบุ')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
                    # Triage section
                    t_scores = patient.get("triage", {})
                    def get_score_label(s):
                        return "🔴 สูง (3)" if s == 3 else ("🟡 กลาง (2)" if s == 2 else ("🟢 ต่ำ (1)" if s == 1 else "🔵 ปกติ (0)"))
                    
                    st.markdown(f"""
                    <div class="print-box">
                        <div class="print-header">🚦 การประเมินความเร่งด่วนรายด้าน (Urgency Triage Scoring - 5 มิติ)</div>
                        <table style="width:100%; border-collapse: collapse; font-size: 13px; text-align: center;" border="1" cellpadding="8" cellspacing="0" bordercolor="#ddd">
                            <tr style="background-color: #F3F4F6; font-weight: bold;">
                                <td style="width:20%;">ร่างกาย (Physical)</td>
                                <td style="width:20%;">จิตใจ (Psychological)</td>
                                <td style="width:20%;">สังคม/ผู้ดูแล (Social)</td>
                                <td style="width:20%;">สิ่งแวดล้อม (Environment)</td>
                                <td style="width:20%;">โภชนาการ (Nutrition)</td>
                            </tr>
                            <tr>
                                <td style="vertical-align: top; padding: 8px;">
                                    <div style="font-size:14px; font-weight:bold; margin-bottom:5px;">{get_score_label(t_scores.get('physical_score', 0))}</div>
                                    <span style="font-size:11px; color:gray;">{t_scores.get('physical_desc', '')}</span>
                                </td>
                                <td style="vertical-align: top; padding: 8px;">
                                    <div style="font-size:14px; font-weight:bold; margin-bottom:5px;">{get_score_label(t_scores.get('psychological_score', 0))}</div>
                                    <span style="font-size:11px; color:gray;">{t_scores.get('psychological_desc', '')}</span>
                                </td>
                                <td style="vertical-align: top; padding: 8px;">
                                    <div style="font-size:14px; font-weight:bold; margin-bottom:5px;">{get_score_label(t_scores.get('social_score', 0))}</div>
                                    <span style="font-size:11px; color:gray;">{t_scores.get('social_desc', '')}</span>
                                </td>
                                <td style="vertical-align: top; padding: 8px;">
                                    <div style="font-size:14px; font-weight:bold; margin-bottom:5px;">{get_score_label(t_scores.get('environment_score', 0))}</div>
                                    <span style="font-size:11px; color:gray;">{t_scores.get('environment_desc', '')}</span>
                                </td>
                                <td style="vertical-align: top; padding: 8px;">
                                    <div style="font-size:14px; font-weight:bold; margin-bottom:5px;">{get_score_label(t_scores.get('nutrition_score', 0))}</div>
                                    <span style="font-size:11px; color:gray;">{t_scores.get('nutrition_desc', '')}</span>
                                </td>
                            </tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
    
                    # Care plan section
                    st.markdown("<div class='print-box'>", unsafe_allow_html=True)
                    st.markdown("<div class='print-header'>📋 ตารางแผนการพยาบาลและการแก้ปัญหา (Nursing Care Plan)</div>", unsafe_allow_html=True)
                    if patient.get("care_plans", []):
                        cp_list = []
                        for cp in patient["care_plans"]:
                            cp_list.append({
                                "วันที่": cp.get("date", "-"),
                                "ปัญหา/ความต้องการ": cp.get("problem", "-"),
                                "เป้าหมาย": cp.get("goal", "-"),
                                "กิจกรรม (Management)": cp.get("management", "-"),
                                "ประเมินผล": cp.get("evaluation", "-")
                            })
                        cp_df = pd.DataFrame(cp_list)
                        st.table(cp_df)
                    else:
                        st.info("ไม่มีรายการแผนพยาบาล")
                    st.markdown("</div>", unsafe_allow_html=True)
    
                    # SECTION 3: Post visit CPR
                    st.markdown(f"""
                    <div class="print-box">
                        <div class="print-header">🏥 แผนระยะยาวและบันทึกสรุปทางการพยาบาล (PHASE 3: POST-HOME VISIT - CPR)</div>
                        <table style="width:100%; border-collapse: collapse; font-size: 14px; margin-bottom: 15px;">
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="width: 50%; vertical-align: top; padding: 8px 0; border-right: 1px solid #eee; padding-right:10px;">
                                    <b>C - Clarify Problems (สรุปปัญหา):</b><br>
                                    <span style="color:red; font-size:13px; font-weight:bold;">• ปัญหาที่กำลังแก้ไข (Active):</span> <span style="font-size:13px;">{patient.get('active_problems', '-')}</span><br>
                                    <span style="color:green; font-size:13px; font-weight:bold;">• ปัญหาคลี่คลาย (Non-active):</span> <span style="font-size:13px;">{patient.get('non_active_problems', '-')}</span>
                                </td>
                                <td style="width: 50%; vertical-align: top; padding: 8px 0; padding-left:15px;">
                                    <b>P - Planning for Future (แผนนัดหมายครั้งหน้า):</b><br>
                                    <span style="font-size:13px;">• วันที่และประเด็น: 
                                    {patient.get('future_plans', [{}])[0].get('topic', '-') if patient.get('future_plans', []) else '-'} 
                                    (เป้าหมาย: {patient.get('future_plans', [{}])[0].get('goal', '-') if patient.get('future_plans', []) else '-'})</span>
                                </td>
                            </tr>
                        </table>
                        
                        <table style="width:100%; border-collapse: collapse; font-size: 14px;">
                            <tr>
                                <td style="width: 50%; vertical-align: top; padding: 12px; border: 1px solid #ddd; background-color: #F9FAFB;">
                                    <b>🧑‍⚕️ บันทึกทางการแพทย์ (Doctor's Note)</b><br>
                                    <span style="font-size: 13px; color: gray;">แพทย์ผู้รับผิดชอบ: {patient.get('doctor_name', '-')}</span><br>
                                    <p style="font-size: 13px; font-style: italic; margin-top: 5px; color: #374151;">"{patient.get('doctor_note', '-')}"</p>
                                </td>
                                <td style="width: 50%; vertical-align: top; padding: 12px; border: 1px solid #ddd; background-color: #ECFDF5;">
                                    <b>👩‍⚕️ สรุปและผลลัพธ์ทางการพยาบาลสุดท้าย (Overall Evaluation)</b><br>
                                    <span style="font-size: 13px; color: gray;">ผลลัพธ์: {patient.get('nursing_outcome', '-')}</span><br>
                                    <p style="font-size: 13px; margin-top: 5px; color: #065F46;">{patient.get('nursing_note', '-')}</p>
                                </td>
                            </tr>
                        </table>
                        
                        <div style="margin-top: 15px; text-align: right; font-size: 13px; color: gray;">
                            <b>ผู้ลงบันทึกรายงานและนัดหมายประสานแผน (Phase 3):</b> {patient.get('responsible_phase3', 'ไม่ได้ระบุ')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
                    # HTML components for automated print popup
                    import streamlit.components.v1 as components
                    components.html("""
                    <script>
                    window.onload = function() {
                        setTimeout(function() {
                            window.parent.focus();
                            window.parent.print();
                        }, 500);
                    }
                    </script>
                    """, height=0, width=0)
                    
                    st.info("💡 **ระบบเปิดมุมมองสั่งพิมพ์สำเร็จ**: ระบบได้ส่งคำสั่งเรียกใช้เครื่องพิมพ์ของอุปกรณ์ท่านขึ้นมาโดยอัตโนมัติแล้วค่ะ (หากหน้าต่างไม่แสดงขึ้นมาโดยอัตโนมัติ กรุณกดปุ่ม **Ctrl + P** สำหรับ Windows หรือ **Cmd + P** สำหรับ Mac เพื่อพิมพ์หรือบันทึกเป็น PDF ได้ทันทีค่ะ)")
                    st.stop()  # Terminate execution early to completely hide tabs and other content!
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📋 Phase 1: ข้อมูลประวัติและการวางแผน (ROPE)",
                    "🏡 Phase 2: ผลการประเมินที่บ้าน (G-TIME & INHOMESSS)",
                    "📊 Phase 3: แผนพยาบาลและผลลัพธ์ (CPR & Care Plan)",
                    "⚙️ จัดการฐานข้อมูล / ลบเคส"
                ])
    
                with tab1:
                    st.subheader("R : Review History (ข้อมูลประวัติส่วนตัวและโรค)")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.write(f"**ชื่อ-นามสกุล:** {patient['name']}")
                        st.write(f"**เลขที่ HN:** {patient['hn']}")
                        st.write(f"**เลขที่ AN:** {patient.get('an', '-')}")
                        st.write(f"**เพศ:** {patient['gender']} | **อายุ:** {patient['age']} ปี")
                        st.write(f"**สถานภาพ:** {patient.get('marriage', '-')}")
                        st.write(f"**การวินิจฉัย (Diagnosis):** :blue[{patient.get('diagnosis', '-')}]")
                    with c2:
                        st.write(f"**ประเภทผู้ป่วย:** :orange[{patient.get('patient_type', '-')}]")
                        st.write(f"**ศาสนา:** {patient.get('religion', '-')}")
                        st.write(f"**โรคประจำตัว (Underlying):** {patient.get('underlying', '-')}")
                        st.write(f"**ประวัติแพ้ยา:** {patient.get('drug_allergy', '-')}")
                        st.write(f"**ประวัติแพ้อาหาร:** {patient.get('food_allergy', '-')}")
                    with c3:
                        st.write(f"**คะแนน ADL:** {patient.get('adl', '-')} คะแนน")
                        st.write(f"**สิทธิ์รักษา:** {patient.get('benefit', '-')}")
                        st.write(f"**เบอร์ติดต่อ:** {patient.get('phone', '-')}")
                        st.write(f"**ผู้ดูแลหลัก:** {patient.get('caregiver', '-')}")
                        st.write(f"**เขต รพ.สต. กำแพงเพชร:** {patient.get('pcsu', '-')}")
                    
                    st.markdown(f"**ที่อยู่:** {patient.get('address', '-')}")
                    st.markdown("---")
                    
                    st.subheader("O, P, E : วัตถุประสงค์ แผน และความพร้อม")
                    cx1, cx2, cx3 = st.columns(3)
                    with cx1:
                        st.markdown("**🎯 วัตถุประสงค์การเยี่ยม:**")
                        for obj in patient.get("objectives", []):
                            st.write(f"- {obj}")
                    with cx2:
                        st.markdown("**🩺 ทีมสหวิชาชีพที่เตรียมแผน:**")
                        for team in patient.get("planning_team", []):
                            st.write(f"- {team}")
                    with cx3:
                        st.markdown("**📦 อุปกรณ์ที่จัดเตรียม:**")
                        for eq in patient.get("equipment", []):
                            st.write(f"- {eq}")
    
                    st.markdown("---")
                    st.markdown(f"✍️ **ผู้รับผิดชอบ PHASE 1 (ROPE):** :green[{patient.get('responsible_phase1', 'ไม่ได้ระบุ')}]")
    
                with tab2:
                    st.subheader("G : Genogram & T : Time")
                    st.write(f"**ผังครอบครัวและบริบทสัมพันธภาพ:** {patient.get('genogram', '-')}")
                    st.write(f"**วันที่ลงเยี่ยมบ้าน:** {patient.get('visit_date', '-')} | **รวมระยะเวลาเยี่ยม:** {patient.get('duration', 0)} นาที ({patient.get('start_time', '')} - {patient.get('end_time', '')})")
                    st.markdown("---")
                    
                    st.subheader("I : การประเมินสภาพแวดล้อม INHOMESSS 9 ด้าน")
                    ci1, ci2, ci3 = st.columns(3)
                    with ci1:
                        st.markdown(f"**1. Immobility:**\n{patient.get('immobility', '-')}")
                        st.markdown(f"**2. Nutrition:**\n{patient.get('nutrition', '-')}")
                        st.markdown(f"**3. Housing:**\n{patient.get('housing', '-')}")
                    with ci2:
                        st.markdown(f"**4. Other People:**\n{patient.get('other_people', '-')}")
                        st.markdown(f"**5. Medication:**\n{patient.get('medication', '-')}")
                        st.markdown(f"**6. Examination:**\n{patient.get('examination', '-')}")
                    with ci3:
                        st.markdown(f"**7. Safety:**\n{patient.get('safety', '-')}")
                        st.markdown(f"**8. Spiritual Health:**\n{patient.get('spiritual', '-')}")
                        st.markdown(f"**9. Service:**\n{patient.get('service', '-')}")
    
                    st.markdown("---")
                    st.markdown(f"✍️ **ผู้รับผิดชอบ PHASE 2 (G-TIME & INHOMESSS):** :green[{patient.get('responsible_phase2', 'ไม่ได้ระบุ')}]")
    
                with tab3:
                    st.subheader("🚦 ผลประเมินความเร่งด่วนรายด้าน (Urgency Triage)")
                    ct1, ct2, ct3, ct4, ct5 = st.columns(5)
                    t_scores = patient.get("triage", {})
                    
                    # Dynamic scoring badges
                    def score_color(s):
                        return "🔴 วิกฤต/สูง (3)" if s == 3 else ("🟡 ปานกลาง (2)" if s == 2 else ("🟢 ต่ำ (1)'" if s == 1 else "🔵 ปกติ (0)"))
                    
                    with ct1:
                        st.metric("ร่างกาย", t_scores.get("physical_score", 0))
                        st.caption(score_color(t_scores.get("physical_score", 0)))
                        st.markdown(f"*{t_scores.get('physical_desc', '')}*")
                    with ct2:
                        st.metric("จิตใจ", t_scores.get("psychological_score", 0))
                        st.caption(score_color(t_scores.get("psychological_score", 0)))
                        st.markdown(f"*{t_scores.get('psychological_desc', '')}*")
                    with ct3:
                        st.metric("สังคม/ญาติ", t_scores.get("social_score", 0))
                        st.caption(score_color(t_scores.get("social_score", 0)))
                        st.markdown(f"*{t_scores.get('social_desc', '')}*")
                    with ct4:
                        st.metric("สิ่งแวดล้อม", t_scores.get("environment_score", 0))
                        st.caption(score_color(t_scores.get("environment_score", 0)))
                        st.markdown(f"*{t_scores.get('environment_desc', '')}*")
                    with ct5:
                        st.metric("โภชนาการ", t_scores.get("nutrition_score", 0))
                        st.caption(score_color(t_scores.get("nutrition_score", 0)))
                        st.markdown(f"*{t_scores.get('nutrition_desc', '')}*")
    
                    st.markdown("---")
                    st.subheader("📋 ตารางแผนการพยาบาลและการแก้ปัญหา (Nursing Care Plan)")
                    if patient.get("care_plans", []):
                        # Align columns to new request
                        cp_list = []
                        for cp in patient["care_plans"]:
                            cp_list.append({
                                "วันที่": cp.get("date", "-"),
                                "ปัญหา/ความต้องการ": cp.get("problem", "-"),
                                "เป้าหมาย": cp.get("goal", "-"),
                                "กิจกรรม (Management)": cp.get("management", "-"),
                                "ประเมินผล": cp.get("evaluation", "-")
                            })
                        cp_df = pd.DataFrame(cp_list)
                        st.table(cp_df)
                    else:
                        st.info("ไม่มีรายการแผนพยาบาล")
    
                    st.markdown("---")
                    st.subheader("🏥 สรุปและแผนระยะถัดไป (CPR & Record)")
                    st.markdown(f"**C - Clarify Problems:**")
                    st.write(f"- 🔴 *Active Problems (กำลังดำเนินงาน):* {patient.get('active_problems', '-')}")
                    st.write(f"- 🟢 *Non-active Problems (แก้ไขสำเร็จ):* {patient.get('non_active_problems', '-')}")
                    
                    st.write("")
                    st.markdown(f"**P - Planning for Future (แผนติดตามงานในอนาคต):**")
                    if patient.get("future_plans", []):
                        fp_df = pd.DataFrame(patient["future_plans"])
                        fp_df.columns = ["วันที่กำหนด", "ประเด็นติดตาม", "เป้าหมายถัดไป", "กิจกรรมทีมสหวิชาชีพ", "ประเมินและลงนาม"]
                        st.table(fp_df)
                    else:
                        st.info("ไม่มีแผนติดตามผลระบุ")
    
                    st.write("")
                    st.markdown(f"**R - Recording (บันทึกสุดท้าย):**")
                    c_doc, c_nur = st.columns(2)
                    with c_doc:
                        st.markdown(f"🧑‍⚕️ **Doctor's Note ({patient.get('doctor_name', '-')})**")
                        st.info(patient.get('doctor_note', 'ไม่มีการลงบันทึกคำสั่งแพทย์'))
                    with c_nur:
                        st.markdown(f"👩‍⚕️ **Nursing Evaluation ({patient.get('nursing_outcome', '-')})**")
                        st.success(patient.get('nursing_note', 'ไม่มีบันทึกรายละเอียดเพิ่มเติม'))
    
                    st.markdown("---")
                    st.markdown(f"✍️ **ผู้รับผิดชอบ PHASE 3 (CPR):** :green[{patient.get('responsible_phase3', 'ไม่ได้ระบุ')}]")
    
                with tab4:
                    st.subheader("⚠️ จัดการเคสผู้ป่วย")
                    st.warning("ระวัง! การดำเนินการลบจะไม่สามารถกู้คืนข้อมูลได้")
                    if st.button("🗑️ ลบแฟ้มประวัติเคสนี้ออกจากฐานข้อมูล", key=f"del_{patient['hn']}"):
                        patients_db.remove(patient)
                        save_data(patients_db)
                        st.success(f"ลบข้อมูลผู้ป่วย {patient['name']} (HN: {patient['hn']}) เรียบร้อยแล้ว ระบบกำลังรีเฟรช...")
                        st.rerun()
    
    # ----------------- PAGE 3: RECORD NEW VISIT -----------------
    elif menu == "➕ บันทึกเคสเยี่ยมบ้านใหม่":
        st.markdown("<h1 style='color: #1E3A8A;'>➕ แบบฟอร์มบันทึกการเยี่ยมบ้านและวางแผนประเมินผล</h1>", unsafe_allow_html=True)
        st.markdown("กรอกข้อมูลให้ครบถ้วนตามขั้นตอนของสหวิชาชีพและแนวทาง ROPE, G-TIME, CPR จังหวัดกำแพงเพชร")
        st.write("")
    
        with st.form("new_visit_form"):
            # Section 1: Review History
            st.markdown("<h3 style='color: #1E3A8A; background-color: #EFF6FF; padding: 6px 12px; border-radius: 4px;'>PHASE 1: PRE-HOME VISIT (ROPE)</h3>", unsafe_allow_html=True)
            st.subheader("R: Review History (ประวัติพื้นฐานคนไข้)")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                hn = st.text_input("เลขที่ HN *", placeholder="HN-XXXXX")
                an = st.text_input("เลขที่ AN", placeholder="AN-XXXXX")
                name = st.text_input("ชื่อ - สกุล ผู้รับบริการ *", placeholder="ระบุชื่อ-สกุล")
                gender = st.selectbox("เพศ", ["ชาย", "หญิง", "อื่นๆ"])
                age = st.number_input("อายุ (ปี)", min_value=0, max_value=130, value=60)
                diagnosis = st.text_input("การวินิจฉัยโรค (Diagnosis) *", placeholder="ระบุการวินิจฉัยทางการแพทย์หลัก")
            
            with c2:
                patient_type = st.selectbox(
                    "ประเภทผู้ป่วย *",
                    ["stroke", "cancer", "ติดเตียง", "ดูแลหลังผ่าตัด", "มารดาหลังคลอด", "จิตเวช", "DM", "HT", "พิการ", "อื่นๆ"]
                )
                marriage = st.selectbox("สถานภาพสมรส", ["โสด", "คู่", "หม้าย", "หย่าร้าง", "แยกกันอยู่"])
                religion = st.text_input("ศาสนา", value="พุทธ")
                
                # Underlying disease checklist/multiselect
                underlying_sel = st.multiselect(
                    "โรคประจำตัว (Underlying Disease)",
                    ["HT", "DM", "Old CVA", "CKD", "HD", "DLP", "อื่นๆ"],
                    default=["HT", "DM"]
                )
                underlying_other = st.text_input("โรคประจำตัวอื่นๆ (ระบุเติมหากเลือก 'อื่นๆ')", "")
                
                drug_allergy = st.text_input("ประวัติแพ้ยา", value="ไม่มี")
                food_allergy = st.text_input("ประวัติแพ้อาหาร/สารอื่นๆ", value="ไม่มี")
                
            with c3:
                # PCSU selectbox with Kamphaeng Phet options
                pcsu_sel = st.selectbox("เขตพื้นที่ รพ.สต. จังหวัดกำแพงเพชร *", KPP_HOSPITALS)
                pcsu_other = st.text_input("รพ.สต. อื่นๆ ใน จ.กำแพงเพชร (กรณีเลือกอื่นๆ)", "")
                
                # ADL slide with dynamic recommended urgency calculation
                adl = st.slider("คะแนน ADL (Barthel Index)", min_value=0, max_value=20, value=20, help="คะแนน 0-20 ยิ่งน้อยยิ่งติดเตียง")
                
                # Show dynamic feedback
                if adl <= 4:
                    st.error("🚨 คะแนน ADL กลุ่มติดเตียง (0-4 คะแนน) -> ระดับความเร่งด่วนสูง (High) ต้องลงเยี่ยมบ้านครั้งแรกด่วนที่สุดภายใน 24-48 ชั่วโมง")
                elif adl <= 11:
                    st.warning("⚠️ คะแนน ADL กลุ่มติดบ้าน (5-11 คะแนน) -> ระดับความเร่งด่วนปานกลาง ควรลงเยี่ยมบ้านครั้งแรกภายใน 1-2 สัปดาห์")
                else:
                    st.success("💚 คะแนน ADL กลุ่มติดสังคม (12-20 คะแนน) -> ปกติ / ความเร่งด่วนต่ำ สามารถลงเยี่ยมตามระบบแผนการดูแลปกติ")
    
                occupation = st.text_input("อาชีพ", placeholder="ระบุอาชีพดั้งเดิมหรือปัจจุบัน")
                income = st.text_input("รายได้ (บาท/เดือน)", placeholder="ระบุตัวเลข เช่น 5000 หรือ ไม่มีรายได้")
                benefit = st.selectbox("สิทธิการรักษา", ["บัตรทอง", "ข้าราชการ/รัฐวิสาหกิจ", "ประกันสังคม", "ชำระเงินเอง", "อื่นๆ"])
    
            c_add1, c_add2 = st.columns([2, 1])
            with c_add1:
                address = st.text_area("ที่อยู่สำหรับการเยี่ยมบ้าน", placeholder="บ้านเลขที่ หมู่ ซอย ถนน ตำบล อำเภอ จังหวัดกำแพงเพชร")
            with c_add2:
                phone = st.text_input("เบอร์โทรศัพท์ติดต่อ", placeholder="08X-XXX-XXXX")
                caregiver = st.text_input("ผู้ดูแลหลัก (Caregiver)", placeholder="ระบุชื่อและความสัมพันธ์ เช่น นาย ก. (ลูกชาย)")
    
            st.markdown("---")
            # Objectives, Planning, Equipment
            st.subheader("O, P, E : วัตถุประสงค์ การวางแผนทีม และความพร้อมอุปกรณ์")
            col_o, col_p, col_e = st.columns(3)
            
            with col_o:
                objectives = st.multiselect(
                    "O : Objectives (วัตถุประสงค์การเยี่ยม) *",
                    ["Long-term care", "ติดตามแผล", "ติดตามการใช้ยา", "ติดต่อแหล่งช่วยเหลือสนับสนุนในชุมชน", "ประเมินพฤทีพรรณดูแลตนเอง"],
                    default=["Long-term care"]
                )
                other_obj = st.text_input("วัตถุประสงค์อื่นๆ (ระบุเพิ่มเติม)", "")
                if other_obj:
                    objectives.append(other_obj)
                    
            with col_p:
                planning_team = st.multiselect(
                    "P : Planning (วิชาชีพในทีมเยี่ยมบ้าน) *",
                    ["พยาบาลวิชาชีพ", "เภสัชกร", "นักกำหนดอาหาร/โภชนากร", "นักกายภาพบำบัด", "แพทย์", "แหล่งช่วยเหลือสนับสนุนอื่นๆ"],
                    default=["พยาบาลวิชาชีพ"]
                )
                other_plan = st.text_input("ทีมวิชาชีพอื่น (ระบุเพิ่มเติม)", "")
                if other_plan:
                    planning_team.append(other_plan)
                    
            with col_e:
                equipment = st.multiselect(
                    "E : Equipment (เครื่องมือเยี่ยมบ้าน) *",
                    ["อุปกรณ์วัด V/S", "อุปกรณ์ทำแผล", "ข้อมูลแหล่งสนับสนุน", "อุปกรณ์ทางการแพทย์เฉพาะตัว", "เวชภัณฑ์พยาบาล"],
                    default=["อุปกรณ์วัด V/S"]
                )
                other_eq = st.text_input("อุปกรณ์อื่น (ระบุเพิ่มเติม)", "")
                if other_eq:
                    equipment.append(other_eq)
    
            # Sign-off Phase 1
            st.markdown("")
            resp_p1 = st.text_input("✍️ ผู้รับผิดชอบ PHASE 1 (ROPE) - (ระบุชื่อผู้บันทึก/วางแผนก่อนเข้าเยี่ยม)", placeholder="เช่น พย.สมศรี วงศ์ดี")
    
            st.write("")
            # Section 2: Home Visit
            st.markdown("<h3 style='color: #1E3A8A; background-color: #EFF6FF; padding: 6px 12px; border-radius: 4px;'>PHASE 2: HOME VISIT (G-TIME)</h3>", unsafe_allow_html=True)
            st.subheader("G : Genogram & T : Time (ผังครอบครัว และเวลาลงเยี่ยม)")
            
            genogram = st.text_area("G: รายละเอียดผังเครือญาติ ครอบครัว โรคกรรมพันธุ์ และความสัมพันธ์", placeholder="ระบุลักษณะการอยู่ร่วมกัน และความเกี่ยวข้องช่วยเหลือของสมาชิกในบ้าน")
            
            cg1, cg2, cg3 = st.columns(3)
            with cg1:
                visit_date = st.date_input("วันที่เข้าเยี่ยมบ้าน", datetime.now())
            with cg2:
                start_time = st.time_input("เวลาเริ่มเข้าเยี่ยมบ้าน", time(9, 0))
            with cg3:
                end_time = st.time_input("เวลาสิ้นสุดการเยี่ยมบ้าน", time(10, 0))
    
            st.markdown("---")
            st.subheader("I : การประเมินสภาพแวดล้อมและบริบทเยี่ยมบ้าน 9 ด้าน (INHOMESSS)")
            
            ci1, ci2, ci3 = st.columns(3)
            with ci1:
                immobility = st.text_area("I - Immobility (การเคลื่อนไหวของผู้ป่วย)", placeholder="เช่น เดินสะดวก, อ่อนแรงครึ่งซีก, อุปกรณ์ช่วยเดิน")
                nutrition = st.text_area("N - Nutrition (พฤติกรรมโภชนาการและการทานอาหาร)", placeholder="เช่น เคี้ยวลำบาก, ให้อาหารสายยาง, ทานเค็ม/หวานจัด")
                housing = st.text_area("H - Housing (สภาพโครงสร้างบ้านความเหมาะสม)", placeholder="เช่น บ้านปูนชั้นเดียว, ทางลาดชัน, ห้องน้ำนอกบ้าน")
            with ci2:
                other_people = st.text_area("O - Other People (ความพร้อมและทัศนคติผู้ดูแล)", placeholder="เช่น ผู้ดูแลมีความตระหนักดี, สมาชิกในบ้านสนับสนุน, ไม่มีผู้ดูแล")
                medication = st.text_area("M - Medication (ระบบการจัดเก็บและพฤติกรรมใช้ยา)", placeholder="เช่น ทานครบตรงเวลา, มีปัญหาลืมยาบ่อย, เก็บยาซ้ำซ้อน")
                examination = st.text_area("E - Examination (ผลตรวจร่างกาย/สัญญาณชีพ)", placeholder="เช่น BP 120/80 mmHg, PR 78 bpm, สภาพแผลประเมิน")
            with ci3:
                safety = st.text_area("S - Safety (ความปลอดภัยในการใช้ชีวิตในที่พัก)", placeholder="เช่น มีความเสี่ยงลื่นล้มทางเดิน, ห้องน้ำลื่น, ไฟมืดเกรงลื่น")
                spiritual = st.text_area("S - Spiritual health (สภาวะจิตวิญญาณและความเชื่อ)", placeholder="เช่น ผู้ป่วยเครียดบ่อย, มีกำลังใจดี, มีศรัทธาสนับสนุน")
                service = st.text_area("S - Service (การเข้าถึงสิทธิและการส่งต่อช่วยเหลือ)", placeholder="เช่น ประสานงาน รพ.สต., ยืมเตียงฟื้นฟูสวัสดิการชุมชน")
    
            st.markdown("---")
            st.subheader("🚦 การจัดลำดับความเร่งด่วนรายด้าน (Urgency Triage Scoring - 5 มิติ)")
            st.markdown("ประเมินความเสี่ยงเพื่อจัดสรรทีมลงพื้นที่ 0 คะแนน = ปกติ, 3 คะแนน = มีความเสี่ยงหรือวิกฤตสูง")
            
            ct1, ct2, ct3 = st.columns(3)
            with ct1:
                p_score = st.selectbox("1. ด้านร่างกาย (Physical Risk)", [0, 1, 2, 3], format_func=lambda x: f"คะแนน {x} (0=ปกติไม่มีภาวะแทรกซ้อน, 3=วิกฤต/อาการรุนแรง)")
                p_desc = st.text_input("รายละเอียด/ทีมสหวิชาชีพที่ดูแลด้านร่างกาย", "พยาบาล, แพทย์")
                
                psy_score = st.selectbox("2. ด้านจิตใจ (Psychological Risk)", [0, 1, 2, 3], format_func=lambda x: f"คะแนน {x} (0=อารมณ์ปกติปรับตัวได้ดี, 3=ซึมเศร้าก้าวร้าวรุนแรง)")
                psy_desc = st.text_input("รายละเอียด/ทีมสหวิชาชีพที่ดูแลด้านจิตใจ", "พยาบาล")
                
            with ct2:
                s_score = st.selectbox("3. ด้านสังคม/ผู้ดูแล (Social Risk)", [0, 1, 2, 3], format_func=lambda x: f"คะแนน {x} (0=ผู้ดูแลระบบครอบครัวพร้อม, 3=ไม่มีผู้ดูแลภาระหนักตึงเครียด)")
                s_desc = st.text_input("รายละเอียด/ทีมสหวิชาชีพที่ดูแลด้านสังคม", "ชุมชน, พยาบาล")
                
                env_score = st.selectbox("4. ด้านสิ่งแวดล้อม (Environment)", [0, 1, 2, 3], format_func=lambda x: f"คะแนน {x} (0=บ้านปลอดภัยดีมาก, 3=ไม่ปลอดภัยเสี่ยงอันตรายร้ายแรง)")
                env_desc = st.text_input("รายละเอียด/ทีมสหวิชาชีพที่ดูแลด้านสิ่งแวดล้อม", "ชุมชน")
                
            with ct3:
                nut_score = st.selectbox("5. ด้านโภชนาการ (Nutrition Risk)", [0, 1, 2, 3], format_func=lambda x: f"คะแนน {x} (0=ทานได้ปกติ BMI สมส่วน, 3=ทุพโภชนาการรุนแรงเสี่ยงสำลักขาดสารอาหาร)")
                nut_desc = st.text_input("รายละเอียด/ทีมสหวิชาชีพที่ดูแลด้านโภชนาการ", "นักโภชนาการ")
    
            # Sign-off Phase 2
            st.markdown("")
            resp_p2 = st.text_input("✍️ ผู้รับผิดชอบ PHASE 2 (G-TIME & INHOMESSS) - (ระบุชื่อผู้ตรวจเยี่ยมและบันทึก)", placeholder="เช่น กภ.วิชัย ใจดี / พย.สมศรี วงศ์ดี")
    
            st.markdown("---")
            # Nursing Care Plan (Table form request)
            st.subheader("📋 ตารางแผนการพยาบาลและการแก้ปัญหา (Nursing Care Plan)")
            st.markdown("กรอกแผนการพยาบาล (ดับเบิลคลิกเพื่อพิมพ์แก้ไขข้อมูล และสามารถกดปุ่ม **Add row** ด้านล่างซ้ายของตารางเพื่อเพิ่มแผนข้อต่อไป)")
            
            # Initialize template DataFrame for data editor
            init_cp_df = pd.DataFrame([
                {
                    "วันที่": visit_date.strftime("%Y-%m-%d"),
                    "ปัญหา/ความต้องการ": "เสี่ยงต่อภาวะแทรกซ้อนเนื่องจาก...",
                    "เป้าหมาย": "ไม่มีภาวะแทรกซ้อน เช่น แผลกดทับ",
                    "กิจกรรม (Management)": "พลิกตะแคงตัวคนไข้ทุก 2 ชม. และสอนผู้ดูแลทำความสะอาดผิวหนัง",
                    "ประเมินผล": "ทำได้"
                }
            ])
            
            care_plan_edited = st.data_editor(
                init_cp_df,
                num_rows="dynamic",
                column_config={
                    "วันที่": st.column_config.TextColumn("วันที่", default=visit_date.strftime("%Y-%m-%d")),
                    "ปัญหา/ความต้องการ": st.column_config.TextColumn("ปัญหา/ความต้องการ *", width="medium"),
                    "เป้าหมาย": st.column_config.TextColumn("เป้าหมาย", width="medium"),
                    "กิจกรรม (Management)": st.column_config.TextColumn("กิจกรรม (Management)", width="large"),
                    "ประเมินผล": st.column_config.SelectboxColumn("ประเมินผล", options=["ทำได้", "ทำไม่ได้"], default="ทำได้")
                },
                key="care_plans_editor"
            )
    
            st.write("")
            # Section 3: Post-visit CPR
            st.markdown("<h3 style='color: #1E3A8A; background-color: #EFF6FF; padding: 6px 12px; border-radius: 4px;'>PHASE 3: POST-HOME VISIT (CPR) & RECORDING</h3>", unsafe_allow_html=True)
            st.subheader("C & P : สรุปปัญหาคงอยู่และแผนในอนาคต")
            
            c_active = st.text_area("Active Problems (ปัญหาที่กำลังแก้ไข/ต้องติดตามต่อ)", placeholder="เช่น ระดับความดันผันผวน, แผลกดทับยังไม่แห้งดี")
            c_non_active = st.text_area("Non-active Problems (ปัญหาที่คลี่คลายแล้วตั้งแต่รอบก่อน)", placeholder="เช่น ความไม่สับสนเรื่องยารอบเช้าแก้ไขแล้ว")
            
            st.markdown("**แผนการติดตามผลครั้งถัดไป**")
            fp_topic = st.text_input("ประเด็นติดตามครั้งต่อไป", placeholder="เช่น ติดตามการทำแผลและบริหารข้อ")
            fp_goal = st.text_input("เป้าหมายครั้งต่อไป", placeholder="เช่น ขอบแผลยุบลง ไม่มีอักเสบติดเชื้อ")
            fp_team = st.text_input("กิจกรรมทีมสหวิชาชีพครั้งถัดไป", placeholder="พยาบาลและนักกายภาพเข้าประเมินซ้ำ")
    
            st.markdown("---")
            st.subheader("R : Recording (บันทึกข้อมูลการเยี่ยมแพทย์และพยาบาล)")
            cr1, cr2 = st.columns(2)
            with cr1:
                doctor_name = st.text_input("ชื่อแพทย์ผู้รับผิดชอบดูแลผู้ป่วย", placeholder="นพ. / พญ. ...")
                doctor_note = st.text_area("บันทึกข้อมูลและคำวินิจฉัยทางการแพทย์ (Doctor's Note)", placeholder="ประเมินการตรวจรักษา และคั่งแนะนำเพิ่มเติมทางการแพทย์")
            with cr2:
                nursing_outcome = st.selectbox(
                    "ผลลัพธ์ทางการพยาบาลสุดท้าย",
                    ["ผู้ป่วยสามารถที่จะดูแลตนเองได้", "ผู้ดูแลสามารถดูแลผู้ป่วยได้", "ลดภาวะแทรกซ้อน", "ลดอัตราพิการ/เสียชีวิต", "อื่นๆ"]
                )
                nursing_note = st.text_area("สรุปบันทึกทางการพยาบาล (Nursing Note)", placeholder="ประเมินทักษะ การเรียนรู้ พฤติกรรม และความก้าวหน้าของผลการดูแล")
    
            # Sign-off Phase 3
            st.markdown("")
            resp_p3 = st.text_input("✍️ ผู้รับผิดชอบ PHASE 3 (CPR) - (ระบุชื่อผู้สรุปผลเยี่ยมและวางแผนอนาคต)", placeholder="เช่น พย.สมศรี วงศ์ดี / นพ.ประวิทย์ รักดี")
    
            # Submit button
            submit_btn = st.form_submit_button("💾 ยืนยันบันทึกแฟ้มประวัติเยี่ยมบ้าน")
            
            if submit_btn:
                if not hn or not name or not diagnosis:
                    st.error("❌ กรุณากรอกข้อมูลสำคัญที่มีสัญลักษณ์ (*) ให้ครบถ้วน (เลขที่ HN, ชื่อคนไข้, และการวินิจฉัยโรค)")
                else:
                    # Calculate duration in minutes
                    t_start = datetime.combine(datetime.today(), start_time)
                    t_end = datetime.combine(datetime.today(), end_time)
                    duration_mins = int((t_end - t_start).total_seconds() / 60)
                    if duration_mins < 0:
                        duration_mins += 1440  # handle overnight visits
                    
                    # Format triage dict
                    triage_dict = {
                        "physical_score": p_score, "physical_desc": p_desc, "physical_team": [t.strip() for t in p_desc.split(",") if t.strip()],
                        "psychological_score": psy_score, "psychological_desc": psy_desc, "psychological_team": [t.strip() for t in psy_desc.split(",") if t.strip()],
                        "social_score": s_score, "social_desc": s_desc, "social_team": [t.strip() for t in s_desc.split(",") if t.strip()],
                        "environment_score": env_score, "environment_desc": env_desc, "environment_team": [t.strip() for t in env_desc.split(",") if t.strip()],
                        "nutrition_score": nut_score, "nutrition_desc": nut_desc, "nutrition_team": [t.strip() for t in nut_desc.split(",") if t.strip()]
                    }
                    
                    # Parse Underlying Diseases list
                    combined_underlying = list([d for d in underlying_sel if d != "อื่นๆ"])
                    if "อื่นๆ" in underlying_sel and underlying_other:
                        combined_underlying.append(underlying_other)
                    underlying_str = ", ".join(combined_underlying) if combined_underlying else "ไม่มี"
                    
                    # Parse PCSU selection
                    final_pcsu = pcsu_sel
                    if pcsu_sel == "อื่นๆ (ระบุเอง)" and pcsu_other:
                        final_pcsu = pcsu_other
    
                    # Parse Care Plan from data editor
                    care_plans_list = []
                    for idx, row in care_plan_edited.iterrows():
                        if row.get("ปัญหา/ความต้องการ"): # Skip empty lines
                            care_plans_list.append({
                                "date": str(row.get("วันที่", visit_date.strftime("%Y-%m-%d"))),
                                "problem": str(row.get("ปัญหา/ความต้องการ")),
                                "goal": str(row.get("เป้าหมาย", "-")),
                                "management": str(row.get("กิจกรรม (Management)", "-")),
                                "evaluation": str(row.get("ประเมินผล", "ทำได้"))
                            })
                        
                    future_plans_list = []
                    if fp_topic:
                        future_plans_list.append({
                            "date": (visit_date + pd.Timedelta(days=30)).strftime("%Y-%m-%d"),
                            "topic": fp_topic,
                            "goal": fp_goal,
                            "team_action": fp_team,
                            "evaluation": "รอนัดหมาย"
                        })
                    
                    # New patient object
                    new_patient = {
                        "hn": hn,
                        "an": an,
                        "name": name,
                        "gender": gender,
                        "age": int(age),
                        "marriage": marriage,
                        "religion": religion,
                        "pcsu": final_pcsu,
                        "diagnosis": diagnosis,
                        "patient_type": patient_type,
                        "adl": int(adl),
                        "occupation": occupation,
                        "income": income,
                        "benefit": benefit,
                        "address": address,
                        "phone": phone,
                        "caregiver": caregiver,
                        "underlying": underlying_str,
                        "drug_allergy": drug_allergy,
                        "food_allergy": food_allergy,
                        "objectives": objectives,
                        "planning_team": planning_team,
                        "equipment": equipment,
                        "responsible_phase1": resp_p1 if resp_p1 else "ไม่ได้ระบุ",
                        "genogram": genogram,
                        "visit_date": visit_date.strftime("%Y-%m-%d"),
                        "start_time": start_time.strftime("%H:%M"),
                        "end_time": end_time.strftime("%H:%M"),
                        "duration": duration_mins,
                        "immobility": immobility,
                        "nutrition": nutrition,
                        "housing": housing,
                        "other_people": other_people,
                        "medication": medication,
                        "examination": examination,
                        "safety": safety,
                        "spiritual": spiritual,
                        "service": service,
                        "responsible_phase2": resp_p2 if resp_p2 else "ไม่ได้ระบุ",
                        "triage": triage_dict,
                        "care_plans": care_plans_list,
                        "responsible_phase3": resp_p3 if resp_p3 else "ไม่ได้ระบุ",
                        "active_problems": c_active,
                        "non_active_problems": c_non_active,
                        "future_plans": future_plans_list,
                        "doctor_name": doctor_name,
                        "doctor_note": doctor_note,
                        "nursing_outcome": nursing_outcome,
                        "nursing_note": nursing_note
                    }
                    
                    # Check for duplicates or update
                    existing_index = next((i for i, p in enumerate(patients_db) if p["hn"] == hn), None)
                    if existing_index is not None:
                        patients_db[existing_index] = new_patient
                        st.success(f"🔄 อัปเดตข้อมูลผู้ป่วยเดิม {name} (HN: {hn}) เรียบร้อยแล้ว")
                    else:
                        patients_db.append(new_patient)
                        st.success(f"🎉 ขึ้นทะเบียนเคสใหม่และบันทึกประวัติการเยี่ยมบ้าน {name} สำเร็จ")
                    
                    save_data(patients_db)
                    st.balloons()
    
    # ----------------- PAGE 4: INFO -----------------
    elif menu == "ℹ️ ข้อมูลระบบเยี่ยมบ้าน":
        st.markdown("<h1 style='color: #1E3A8A;'>ℹ️ ข้อมูลระบบบันทึกและประเมินผลการเยี่ยมบ้าน</h1>", unsafe_allow_html=True)
        
        st.markdown("""
        แอปพลิเคชันเวอร์ชัน v2 นี้ได้รับการพัฒนาและปรับปรุงให้มีความจำเพาะต่อสุขอนามัยในพื้นที่และการทำงานของทีมเยี่ยมบ้าน จังหวัดกำแพงเพชร โดยใช้หลักการโครงสร้างกระบวนการดูแลในชุมชนผ่านทีมสหวิชาชีพ 3 ระยะหลัก (Phases):
        
        * **PHASE 1: PRE-HOME VISIT (ROPE)**
            * **R (Review History)**: ทบทวนวิเคราะห์ประวัติ ความเจ็บป่วย ผล ADL, ประเภทผู้ป่วยหลัก (stroke, cancer, จิตเวช ฯลฯ) และ Diagnosis โรคทางการแพทย์อย่างเป็นระบบ
            * **O (Objectives)**: กำหนดเป้าหมายที่ชัดเจนก่อนเดินทาง เช่น เฝ้าระวังแผล, จัดการยา
            * **P (Planning)**: มอบหมายหน้าที่ สหวิชาชีพจัดทีมให้ตอบโจทย์ปัญหาของคนไข้
            * **E (Equipment)**: จัดเตรียมความสมบูรณ์ของเครื่องมือเวชภัณฑ์และทรัพยากรช่วยเหลือ
            * **ผู้รับผิดชอบ PHASE 1**: ลงชื่อพยาบาลหรือวิชาชีพผู้บันทึกประวัติและการเตรียมตัวก่อนลงพื้นที่
            
        * **PHASE 2: HOME VISIT (G-TIME & INHOMESSS)**
            * **G (Genogram)**: ผังเครือญาติ วิเคราะห์กรรมพันธุ์ ความผูกพัน และแนวรับในครอบครัว
            * **T (Time)**: บันทึกระยะเวลาในการเยี่ยม โดยแอปคำนวณระยะเวลารวมในบ้านให้อัตโนมัติ
            * **I (INHOMESSS)**: โครงสร้างประเมินปัจจัยสิ่งแวดล้อม 9 มิติเพื่อความปลอดภัยของผู้ป่วย
            * **Urgency Triage Scoring**: คัดกรองและประเมินความเร่งด่วน 5 มิติ (ร่างกาย, จิตใจ, สังคม, สิ่งแวดล้อม, โภชนาการ)
            * **Nursing Care Plan**: ตารางแผนการพยาบาลแบบไดนามิก ปรับให้บันทึก ปัญหา เป้าหมาย กิจกรรม และการประเมินผลแยกเป็นรายข้อ
            * **ผู้รับผิดชอบ PHASE 2**: ลงชื่อวิชาชีพผู้ทำการตรวจรักษาและลงบันทึกในบ้านผู้ป่วยจริง
            
        * **PHASE 3: POST-HOME VISIT (CPR)**
            * **C (Clarify Problems)**: แยกแยะปัญหา Active/Non-active และติดตามผลการพยาบาลรายข้อว่า 'ทำได้' หรือ 'ทำไม่ได้'
            * **P (Planning for Future)**: วางเป้าหมายการลงพื้นที่ในครั้งถัดไปร่วมกับทีม
            * **R (Recording)**: ตรวจสอบและประสานผลสรุป บันทึกการพยาบาล และ Doctor's Note
            * **ผู้รับผิดชอบ PHASE 3**: ลงชื่อผู้สรุปรายงานและประชุมทีมสหวิชาชีพหลังกลับมายังหน่วยบริการ
        """)
        
        st.success("👨‍⚕️ ระบบนี้ออกแบบขึ้นตามแนวปฏิบัติการเยี่ยมบ้านอย่างมีทักษะระดับมืออาชีพ เพื่อเป็นแพลตฟอร์มบริหารข้อมูลทางระบาดวิทยาชุมชนให้มีประสิทธิภาพสูงสุด")