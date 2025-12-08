import argparse
import json
import os
import sys
import yaml
from datetime import datetime
from pathlib import Path

# Mock Agent Classes for the Kernel Simulation
class ArchitectAgent:
    def analyze(self, goal, manifest):
        print(f"   [Architect] Analyzing goal: '{goal}'")
        print(f"   [Architect] Reading manifest version {manifest.get('version')}")
        # Simulate task creation
        task_id = f"T-{int(datetime.now().timestamp())}"
        task = {
            "id": task_id,
            "goal": goal,
            "status": "planned",
            "steps": [
                "Identify relevant modules",
                "Draft code changes",
                "Verify against forbidden zones"
            ]
        }
        return task

class CodegenAgent:
    def execute(self, task, manifest):
        print(f"   [Codegen] Executing task {task['id']}...")
        print("   [Codegen] Checking forbidden zones...")
        forbidden = manifest.get("builder_kernel", {}).get("forbidden_zones", [])
        print(f"   [Codegen] avoiding: {forbidden}")
        
        # Simulate code generation
        patch = {
            "file": "core/agents/new_agent.py",
            "content": "# New agent code here"
        }
        print(f"   [Codegen] Generated patch for {patch['file']}")
        return patch

class ReleaseManager:
    def verify_and_merge(self, patch):
        print("   [ReleaseManager] Running tests...")
        # Simulate pytest
        tests_passed = True 
        if tests_passed:
            print("   [ReleaseManager] Tests PASSED (green).")
            print(f"   [ReleaseManager] Merging {patch['file']}...")
            return True
        else:
            print("   [ReleaseManager] Tests FAILED.")
            return False

def load_manifest():
    manifest_path = Path("spec/system_manifest.yaml")
    if not manifest_path.exists():
        print("Error: spec/system_manifest.yaml not found.")
        sys.exit(1)
    with open(manifest_path, "r") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="Earnetics Builder Kernel")
    parser.add_argument("--goal", required=True, help="The goal for this sprint/run")
    args = parser.parse_args()

    print("🚀 EARNETICS BUILDER KERNEL INITIALIZED")
    print(f"🎯 Goal: {args.goal}")
    
    # 1. Load Manifest
    manifest = load_manifest()
    
    # 2. Architect Phase
    architect = ArchitectAgent()
    task = architect.analyze(args.goal, manifest)
    
    # Save task
    tasks_dir = Path("builder/tasks")
    tasks_dir.mkdir(parents=True, exist_ok=True)
    task_file = tasks_dir / f"{task['id']}.json"
    with open(task_file, "w") as f:
        json.dump(task, f, indent=2)
    print(f"   [Kernel] Task saved to {task_file}")

    # 3. Codegen Phase
    codegen = CodegenAgent()
    patch = codegen.execute(task, manifest)
    
    # 4. Release Phase
    release_manager = ReleaseManager()
    success = release_manager.verify_and_merge(patch)
    
    if success:
        print("\n✅ KERNEL RUN COMPLETE: SUCCESS")
    else:
        print("\n❌ KERNEL RUN FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
