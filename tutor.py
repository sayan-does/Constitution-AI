import os
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import requests
import json
import base64
import time
from typing import List, Dict


class MathQuestionGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def extract_text_and_images(self, pdf_path: str) -> List[Dict]:
        doc = fitz.open(pdf_path)
        content = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            images = []
            image_list = page.get_images()
            for img in image_list:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                images.append(image_base64)
            content.append({'text': text, 'images': images})
        doc.close()
        return content

    def generate_questions(self, syllabus_text: str, marks: int) -> List[str]:
        prompt = f"""Generate 3 unique mathematics questions for Class 7 students based on the following syllabus:
        {syllabus_text}
        The questions should be appropriate for the grade level, have clear marking criteria, include a mix of theoretical and application-based questions, and be properly formatted with subparts if needed.
        Please provide the questions in a numbered list."""
        response = requests.post(
            self.openrouter_url,
            headers=self.headers,
            json={
                "model": "anthropic/claude-3-haiku-20240307",
                "messages": [
                    {"role": "system",
                        "content": "You are a mathematics teacher creating exam questions."},
                    {"role": "user", "content": prompt}
                ]
            }
        )
        if response.status_code == 200:
            questions = response.json(
            )['choices'][0]['message']['content'].split('\n')
            return [q.strip() for q in questions if q.strip()]
        return []

    def create_question_paper(self, syllabus_text: str, output_file: str):
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Class 7 Mathematics Question Bank\n\n")
            for marks in [2, 3, 5]:
                f.write(f"{marks} Marks Questions:\n")
                questions = self.generate_questions(syllabus_text, marks)
                for i, question in enumerate(questions, 1):
                    f.write(f"Q{i}. {question}\n")
                f.write("\n")
            f.write("\n" + "-" * 50 + "\n")


def main():
    api_key = "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"
    generator = MathQuestionGenerator(api_key)
    pdf_path = input("Enter the path to your PDF syllabus: ")
    try:
        print("Extracting content from PDF...")
        content = generator.extract_text_and_images(pdf_path)
        syllabus_text = "\n".join([page['text'] for page in content])
        print("Generating questions...")
        output_file = "math_question_bank.txt"
        generator.create_question_paper(syllabus_text, output_file)
        print(f"Question bank has been generated successfully: {output_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
