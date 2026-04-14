#!/usr/bin/env python3
"""
Synthetic Dataset Generator for Security‑Aware Web Architecture Reverse Engineering

Generates a JSONL file containing:
- instruction: a prompt for the model
- input: tech stack and requested features
- output: annotated directory structure with data‑flow and vulnerability hints
"""

import json
import random
import uuid
from typing import Dict, List, Tuple, Optional

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

NUM_SAMPLES = 1200  # Generate at least 1000 entries
OUTPUT_FILE = "web_arch_security_dataset.jsonl"

# Tech stack options
TECH_STACKS = ["Node.js", "Go", "Python/Django", "Rust"]

# Security components that can be mixed and matched
FEATURES = {
    "fingerprinting": ["JA3", "JA4", "HTTP/2_Fingerprint", "TLS_Fingerprint"],
    "ai_pipeline": ["ML_Classifier", "Anomaly_Detection", "Behavior_Analysis"],
    "deception": ["Tarpit", "Honeypot", "Canary_Token", "Decoy_Endpoint"],
    "pipeline_stages": ["PreFilter", "RateLimit", "RiskAnalysis", "Challenge"],
}

# Possible vulnerability hints (injected as comments)
VULN_HINTS = [
    "⚠️ IDOR risk: {file} does not validate object ownership before access",
    "⚠️ Broken auth: {file} uses predictable session tokens",
    "⚠️ Logic bypass: {file} can be skipped by omitting the 'X-Forwarded-For' header",
    "⚠️ Exposure: {file} leaks internal IP in error messages",
    "⚠️ Misconfiguration: {file} disables TLS verification for internal calls",
    "⚠️ Timing attack: {file} uses non‑constant‑time string comparison",
    "⚠️ Path traversal: {file} concatenates user input without sanitization",
]

# ------------------------------------------------------------------------------
# Directory Structure Templates per Tech Stack
# ------------------------------------------------------------------------------

BASE_TEMPLATES = {
    "Node.js": {
        "root": [
            "src/",
            "config/",
            "tests/",
            "scripts/",
            "package.json",
            ".env.example",
        ],
        "src": [
            "index.js",
            "app.js",
            "routes/",
            "controllers/",
            "middleware/",
            "services/",
            "utils/",
            "pipeline/",
            "deception/",
            "fingerprint/",
            "ai/",
        ],
    },
    "Go": {
        "root": [
            "cmd/",
            "internal/",
            "pkg/",
            "configs/",
            "scripts/",
            "go.mod",
            "go.sum",
            ".env",
        ],
        "cmd": ["main.go"],
        "internal": [
            "handlers/",
            "middleware/",
            "pipeline/",
            "deception/",
            "fingerprint/",
            "ai/",
            "models/",
        ],
    },
    "Python/Django": {
        "root": [
            "manage.py",
            "requirements.txt",
            "config/",
            "apps/",
            "templates/",
            "static/",
            "media/",
            ".env",
        ],
        "config": ["settings.py", "urls.py", "wsgi.py"],
        "apps": [
            "core/",
            "api/",
            "pipeline/",
            "deception/",
            "fingerprint/",
            "ai/",
        ],
        "apps/core": ["models.py", "views.py", "admin.py"],
    },
    "Rust": {
        "root": [
            "Cargo.toml",
            "Cargo.lock",
            "src/",
            "tests/",
            "config/",
            ".env",
        ],
        "src": [
            "main.rs",
            "lib.rs",
            "handlers/",
            "middleware/",
            "pipeline/",
            "deception/",
            "fingerprint/",
            "ai/",
            "models/",
        ],
    },
}

# ------------------------------------------------------------------------------
# File Generation Logic
# ------------------------------------------------------------------------------

def generate_file_content(tech: str, file_path: str, features: Dict) -> str:
    """
    Return a placeholder description for a file based on its path and active features.
    This helps the LLM understand the role of each file.
    """
    path_lower = file_path.lower()
    if "fingerprint" in path_lower:
        if "ja3" in path_lower or "ja4" in path_lower:
            return f"# {tech} – Fingerprinting module extracting JA3/JA4 signatures from TLS handshake."
        return f"# {tech} – TLS/HTTP2 fingerprinting logic."
    elif "ai" in path_lower or "ml" in path_lower:
        return f"# {tech} – ML classifier / anomaly detection engine."
    elif "deception" in path_lower or "tarpit" in path_lower or "honeypot" in path_lower:
        return f"# {tech} – Deception handler (tarpit / honeypot / canary)."
    elif "pipeline" in path_lower:
        return f"# {tech} – Request pipeline stage: {path_lower.split('/')[-1]}"
    elif "middleware" in path_lower:
        return f"# {tech} – Middleware component."
    elif "route" in path_lower or "controller" in path_lower or "handler" in path_lower:
        return f"# {tech} – Route handler / controller."
    else:
        return f"# {tech} – Core application logic."

def generate_directory_tree(tech: str, selected_features: Dict) -> str:
    """
    Build a textual directory tree with files, optional descriptions,
    data‑flow arrows (→), and vulnerability hints.
    """
    template = BASE_TEMPLATES[tech]
    lines = []

    def add_dir(path: str, children: List[str], indent: int = 0):
        prefix = "    " * indent
        lines.append(f"{prefix}{path}/")
        for child in sorted(children):
            if child.endswith("/"):
                sub_children = template.get(child.rstrip("/"), [])
                add_dir(child, sub_children, indent + 1)
            else:
                lines.append(f"{prefix}    {child}")
                # Add a short comment about the file's role
                desc = generate_file_content(tech, f"{path}/{child}" if path != "." else child, selected_features)
                lines.append(f"{prefix}        {desc}")

    # Start with root
    root_children = template["root"]
    lines.append(".")
    for item in sorted(root_children):
        if item.endswith("/"):
            sub_children = template.get(item.rstrip("/"), [])
            add_dir(item, sub_children, 1)
        else:
            lines.append(f"    {item}")
            desc = generate_file_content(tech, item, selected_features)
            lines.append(f"        {desc}")

    # Add data‑flow arrows based on selected pipeline stages
    lines.append("\n# Data Flow (→ indicates request propagation)")
    flow_parts = []
    if "pipeline_stages" in selected_features:
        stages = selected_features["pipeline_stages"]
        # Order typical pipeline stages
        order = ["PreFilter", "RateLimit", "Fingerprint", "RiskAnalysis", "Challenge"]
        for stage in order:
            if stage.lower() in [s.lower() for s in stages]:
                flow_parts.append(f"{tech.lower()}/{stage.lower()}.js")
        if "ai_pipeline" in selected_features:
            flow_parts.append("ai/classifier.py" if tech == "Python/Django" else "ai/classifier.go")
        if "deception" in selected_features:
            flow_parts.append("deception/tarpit.rs" if tech == "Rust" else "deception/tarpit.js")
    if flow_parts:
        lines.append("# " + " → ".join(flow_parts))

    # Inject a subtle vulnerability hint
    hint = random.choice(VULN_HINTS)
    hint_file = random.choice([line for line in lines if line.strip().startswith("    ") and not line.strip().endswith("/")])
    if hint_file:
        hint_text = hint.format(file=hint_file.strip())
        lines.append(f"\n# {hint_text}")

    return "\n".join(lines)

# ------------------------------------------------------------------------------
# Feature Selection and Variation
# ------------------------------------------------------------------------------

def select_features() -> Dict:
    """Randomly enable/disable features with some mandatory combinations."""
    features = {}
    # Always include at least one fingerprinting method
    features["fingerprinting"] = random.sample(FEATURES["fingerprinting"], k=random.randint(1, 2))
    # AI pipeline is optional but common
    if random.random() < 0.7:
        features["ai_pipeline"] = random.sample(FEATURES["ai_pipeline"], k=random.randint(1, 2))
    # Deception: 50% chance
    if random.random() < 0.5:
        features["deception"] = random.sample(FEATURES["deception"], k=random.randint(1, 2))
    # Pipeline stages: pick a few
    features["pipeline_stages"] = random.sample(FEATURES["pipeline_stages"], k=random.randint(2, 4))
    return features

def build_input_string(tech: str, features: Dict) -> str:
    """Construct the 'input' field as a concise description."""
    parts = [f"Tech: {tech}"]
    if "fingerprinting" in features:
        parts.append(f"Fingerprinting: {', '.join(features['fingerprinting'])}")
    if "ai_pipeline" in features:
        parts.append(f"AI Pipeline: {', '.join(features['ai_pipeline'])}")
    if "deception" in features:
        parts.append(f"Deception: {', '.join(features['deception'])}")
    if "pipeline_stages" in features:
        parts.append(f"Pipeline: {', '.join(features['pipeline_stages'])}")
    return ", ".join(parts)

# ------------------------------------------------------------------------------
# Instruction Generation
# ------------------------------------------------------------------------------

INSTRUCTION_TEMPLATES = [
    "Generate a high-efficiency anti-bot engine architecture.",
    "Design a web application firewall (WAF) with advanced fingerprinting and deception.",
    "Create a secure API gateway structure with AI-based anomaly detection.",
    "Outline the directory layout and request flow for a fraud detection service.",
    "Produce a blueprint for a reverse‑engineering resistant authentication service.",
    "Sketch the skeleton of a privacy‑preserving analytics pipeline.",
]

def generate_instruction() -> str:
    """Pick a random instruction from the template list."""
    return random.choice(INSTRUCTION_TEMPLATES)

# ------------------------------------------------------------------------------
# Main Generation Loop
# ------------------------------------------------------------------------------

def main():
    random.seed(42)  # For reproducibility
    dataset = []

    for _ in range(NUM_SAMPLES):
        tech = random.choice(TECH_STACKS)
        features = select_features()
        instruction = generate_instruction()
        input_str = build_input_string(tech, features)
        output_str = generate_directory_tree(tech, features)

        entry = {
            "instruction": instruction,
            "input": input_str,
            "output": output_str,
        }
        dataset.append(entry)

    # Shuffle to avoid any ordering bias
    random.shuffle(dataset)

    # Write to JSONL
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for entry in dataset:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✅ Generated {len(dataset)} samples and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
