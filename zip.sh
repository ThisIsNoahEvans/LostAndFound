zip -r submission.zip . \
  -x ".git/*" \
     ".pytest_cache/*" \
     "__pycache__/*" \
     "*.pyc" \
     "bin/*" \
     "lib/*" \
     "include/*" \
     "share/*" \
     ".venv/*" \
     "venv/*" \
     "env/*" \
     ".DS_Store" \
     "README.md" \
     "docs/*" \
     "**/__pycache__/*" \
     "pyvenv.cfg" \
     "lost_and_found.db" \
     "submission.zip" \
     "zip.sh"