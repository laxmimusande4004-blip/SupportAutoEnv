# 🚀 Meta Hackathon: Final Submission Guide

Follow this checklist to ensure your project meets all requirements and is successfully submitted.

## 1. Final Code Audit (Checklist)

Before you upload anything, verify these 5 things:

- [x] **OpenEnv Compliance**: `env.py` has `step()`, `reset()`, and `state()` methods.
- [x] **Pydantic Models**: `models.py` uses Pydantic for Observation, Action, and Reward.
- [x] **3 Tasks**: Easy, Medium, and Hard tasks are defined in `graders.py`.
- [x] **Baseline Inference**: `inference.py` runs successfully and reads `HF_TOKEN`.
- [x] **Dockerfile**: Your Dockerfile builds and runs the FastAPI server on port 8000.

---

## 2. Deploy to Hugging Face Spaces (Mandatory/Highly Recommended)

Judges use Hugging Face to quickly test your environment.

1.  **Create Space**: Go to [huggingface.co/new-space](https://huggingface.co/new-space).
2.  **Settings**:
    *   **SDK**: Select **Docker**.
    *   **Template**: Blank / None.
    *   **Visibility**: Public.
3.  **Upload Variables**:
    *   Go to **Settings > Variables and secrets**.
    *   Add a **Secret** named `HF_TOKEN` with your OpenAI API Key.
4.  **Push Code**: Use `git push` or the Hugging Face web interface to upload all project files.
5.  **Add Tag**: In your Space's `README.md` (metadata section), add `tags: [openenv]`.

---

## 3. Submit on Unstop Platform

The official submission happens on the [Unstop Portal](https://unstop.com/).

### Prepare the ZIP
- Right-click your project folder -> **Compress to ZIP**.
- **IMPORTANT**: Delete the `.venv` and `__pycache__` folders before zipping to keep it small.

### The Submission Form
Fill in the following:
1.  **GitHub URL**: Link to your public repository.
2.  **Hugging Face Space URL**: Link to your active Space (e.g., `huggingface.co/spaces/user/SupportAutoEnv`).
3.  **Project ZIP**: Upload the `.zip` file you created.
4.  **Demo Video (Optional)**: If you recorded a screen share of the inference script running, upload it!

---

## 4. Run Final Validation Command

If you have the `openenv` CLI tool, run this one last time:
```bash
openenv validate openenv.yaml
```

If it says **"Validation Successful"**, you are ready to WIN! 🏆
