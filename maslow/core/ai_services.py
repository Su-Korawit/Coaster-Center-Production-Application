"""
AI Services for Maslow - The Why Ladder & Smart Challenger
Uses Google Gemini API
"""
import google.generativeai as genai
from django.conf import settings
import json
import re


class MaslowAI:
    """AI service for goal transformation and motivation discovery"""
    
    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def _generate(self, prompt: str) -> str:
        """Generate response from Gemini"""
        if not self.model:
            return self._fallback_response(prompt)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"AI Error: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback when API is not available"""
        if "ทำไป" in prompt or "เพื่ออะไร" in prompt:
            return "ผลลัพธ์นี้จะทำให้คุณรู้สึกอย่างไร?"
        return "เป้าหมายที่ยอดเยี่ยม!"
    
    def ask_why(self, goal: str, previous_answers: list = None) -> str:
        """
        The Why Ladder - Ask 'why' to dig deeper into motivation
        """
        context = ""
        if previous_answers:
            context = f"\nคำตอบก่อนหน้า: {', '.join(previous_answers)}"
        
        prompt = f"""คุณเป็น Life Coach ผู้เชี่ยวชาญในการช่วยคนค้นหาแรงจูงใจที่แท้จริง

เป้าหมายของผู้ใช้: {goal}{context}

ให้ถามคำถาม "ทำไป" สั้นๆ เพียง 1 คำถาม เพื่อขุดหาเหตุผลที่ลึกซึ้งกว่า
ใช้ภาษาไทยที่เป็นกันเอง อบอุ่น และกระตุ้นให้คิด

ตอบเพียงคำถามเดียว ไม่ต้องมีคำอธิบายเพิ่ม"""

        return self._generate(prompt)
    
    def transform_goal(self, original_goal: str, motivations: list) -> dict:
        """
        Transform goal into a powerful, inspiring version
        """
        motivation_text = " → ".join(motivations) if motivations else original_goal
        
        prompt = f"""คุณเป็น Life Coach ช่วยแปลงเป้าหมายให้มีพลังและกินใจ

เป้าหมายเดิม: {original_goal}
เส้นทางแรงจูงใจ: {motivation_text}

จากข้อมูลข้างต้น ให้:
1. สรุปแรงจูงใจที่แท้จริง (deep_motivation) - สั้นกระชับ 1 ประโยค
2. สร้างเป้าหมายใหม่ (transformed_goal) ที่:
   - เป็นนามธรรมมากขึ้น
   - สร้างแรงบันดาลใจ
   - ไม่ใช่งานบ้าน แต่คือความฝัน
   - ยาวไม่เกิน 2 ประโยค

ตอบในรูปแบบ JSON:
{{"deep_motivation": "...", "transformed_goal": "..."}}"""

        response = self._generate(prompt)
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        # Fallback
        return {
            "deep_motivation": motivations[-1] if motivations else original_goal,
            "transformed_goal": f"สร้าง {original_goal} เพื่อชีวิตที่ดีกว่า"
        }
    
    def suggest_targets(self, activity: str, baseline: int, unit: str) -> dict:
        """
        Smart Challenger - Generate 3 levels of goals
        """
        prompt = f"""คุณเป็น Personal Trainer ช่วยตั้งเป้าหมายที่เหมาะสม

กิจกรรม: {activity}
ปัจจุบันทำได้: {baseline} {unit}

ให้เสนอ 3 ระดับเป้าหมายตามหลัก Goal Gradient Effect:
- safe: เพิ่มขึ้นเล็กน้อย (ประมาณ 10-30%) - เหมาะสำหรับเริ่มต้น
- growth: ท้าทายพอดี (ประมาณ 50-100%) - แนะนำระดับนี้
- stretch: ท้าทายมาก (ประมาณ 150-200%) - สำหรับคนต้องการท้าทายตัวเอง

ตอบเป็น JSON format เท่านั้น:
{{"safe": <number>, "growth": <number>, "stretch": <number>}}"""

        response = self._generate(prompt)
        
        try:
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "safe": int(result.get("safe", baseline * 1.2)),
                    "growth": int(result.get("growth", baseline * 1.5)),
                    "stretch": int(result.get("stretch", baseline * 2))
                }
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Fallback calculation
        return {
            "safe": int(baseline * 1.2) if baseline > 0 else 1,
            "growth": int(baseline * 1.5) if baseline > 0 else 2,
            "stretch": int(baseline * 2) if baseline > 0 else 5
        }


# Singleton instance
maslow_ai = MaslowAI()
