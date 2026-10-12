SRDM SATNA - श्रमिक नियोजन मॉड्यूल
=================================

यह मॉड्यूल FY 2025-26 के अगस्त + सितम्बर में सृजित मानव दिवस को लक्ष्य मानता है।
स्थायी 8-Janpad लक्ष्य कुल: 2,83,077 मानव दिवस।

FY 2026-27 उपलब्धि Official Employment Provided / Persondays report से आती है।

Difference = अधिकतम (0, लक्ष्य - उपलब्धि)
प्रतिदिन आवश्यकता = Difference / 30 सितम्बर तक शेष दिन
125% दैनिक लक्ष्य = प्रतिदिन आवश्यकता x 1.25

ONE_CLICK_DASHBOARD_DATA_UPDATE.bat अब इन reports को साथ update करता है:
1. R6.9 Daily Monitoring
2. Muster Roll और e-MB
3. श्रमिक नियोजन Persondays
4. Yuktdhara
5. VB-G RAM G Block Statistics

यदि portal का Digest बदल जाए, Command Prompt में नया URL इस प्रकार सेट करें:
set "SHRAMIK_FY2627_URL=FY 2026-27 का पूरा Employment Provided URL"

Sub Engineer-wise सही पुराना लक्ष्य लेने के लिए FY 2025-26 का पूरा report URL दें:
set "SHRAMIK_FY2526_URL=FY 2025-26 का पूरा Employment Provided URL"

इसके बाद ONE_CLICK_DASHBOARD_DATA_UPDATE.bat चलाएँ।

सुरक्षा: किसी live source के fail होने पर उसकी पिछली valid data file सुरक्षित रहती है।
