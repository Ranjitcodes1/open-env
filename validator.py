"""
Pre-submission validation script for StyleSenseEnv.
Strictly checks all requirements from the pre-submission checklist.
"""

import os
import sys
import yaml
import requests
import json
from env.models import OutfitAction, Observation

def check_file_exists(path):
    if os.path.exists(path):
        print(f"✅ FOUND: {path}")
        return True
    else:
        print(f"❌ MISSING: {path}")
        return False

def check_inference_script():
    print("\n--- Checking inference.py ---")
    if not check_file_exists("inference.py"):
        return False
    
    with open("inference.py", "r") as f:
        content = f.read()
        
    mandatory_strings = ["[START]", "[STEP]", "[END]", "API_BASE_URL", "MODEL_NAME", "HF_TOKEN", "OpenAI"]
    all_present = True
    for s in mandatory_strings:
        if s in content:
            print(f"✅ Found mandatory requirement: {s}")
        else:
            print(f"❌ Missing mandatory requirement in inference.py: {s}")
            all_present = False
    return all_present

def check_openenv_spec():
    print("\n--- Checking OpenEnv Compliance ---")
    if not check_file_exists("openenv.yaml"):
        return False
        
    with open("openenv.yaml", "r") as f:
        spec = yaml.safe_load(f)
        
    required_keys = ["name", "version", "tasks", "endpoints"]
    for k in required_keys:
        if k in spec:
            print(f"✅ Spec field present: {k}")
        else:
            print(f"❌ Spec field missing: {k}")
            return False
            
    if len(spec.get("tasks", [])) < 3:
        print(f"❌ At least 3 tasks are required. Found {len(spec.get('tasks', []))}")
        return False
    else:
        print(f"✅ Found {len(spec.get('tasks', []))} tasks.")
    return True

def check_dockerfile():
    print("\n--- Checking Dockerfile ---")
    if not check_file_exists("Dockerfile"):
        return False
    
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    if "7860" in content:
        print("✅ Dockerfile exposes port 7860")
    else:
        print("❌ Dockerfile might not expose port 7860 (standard for HF Spaces)")
    return True

def run_local_validation():
    print("=== StyleSenseEnv PRE-SUBMISSION VALIDATION ===")
    
    tasks = [
        check_inference_script(),
        check_openenv_spec(),
        check_dockerfile(),
        check_file_exists("requirements.txt"),
        check_file_exists("server.py")
    ]
    
    if all(tasks):
        print("\n🏆 ALL PRE-SUBMISSION CHECKLIST ITEMS PASSED! 🏆")
        print("You are ready to submit to HF Spaces.")
    else:
        print("\n🚨 SOME CHECKLIST ITEMS FAILED. Please fix them before submitting. 🚨")
        sys.exit(1)

if __name__ == "__main__":
    run_local_validation()
