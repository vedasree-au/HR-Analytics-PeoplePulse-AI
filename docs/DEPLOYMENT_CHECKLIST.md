# Deployment checklist
- [ ] Run `pytest -q`.
- [ ] Run `streamlit run app.py` and inspect every page.
- [ ] Ensure data CSVs are included.
- [ ] Do not commit `.env`, `.venv`, secrets or local database files.
- [ ] Deploy `app.py` on Streamlit Community Cloud.
- [ ] Test the public URL in a private browser.
- [ ] Add screenshots and demo URL to README after deployment.
