#!/usr/bin/env python3
"""
run_pipeline.py
Master pipeline: PRS → Risk Aggregation → Action Protocol
"""

print("🚀 Starting DNA Virtual Lab Pipeline...\n")

import subprocess

subprocess.run(["python3", "engine/prs_engine.py"])
subprocess.run(["python3", "engine/risk_aggregator.py"])
subprocess.run(["python3", "engine/action_mapper.py"])

print("\n✅ Full pipeline complete. Check reports/ folder for outputs.")