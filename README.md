# Health AI Governance Observatory

Client-facing prototype connecting public health-AI risk signals to governance/ethics principles and concrete mitigations.

## Test in VS Code
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python collector.py
streamlit run app.py
```

`collector.py` must run successfully before the app because no dummy dataset is bundled.

## Deploy
Push the folder contents to a GitHub repository. Run the included Actions workflow manually once, then deploy `app.py` to Streamlit Community Cloud. The workflow refreshes the dataset every six hours.

## Important
Mappings express principles potentially at risk unless evidence supports a stronger conclusion. The tool is governance intelligence, not medical advice, legal advice or a clinical safety certification.
