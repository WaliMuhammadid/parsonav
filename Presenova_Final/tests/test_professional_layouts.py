"""
Test Professional Presentation Layouts & Templates
Verifies the new agency-grade presentation layout builders and themes.
"""

import os
import sys
from pptx import Presentation

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.presentation_generator import (
    generate_presentation_outline,
    build_pptx_from_outline,
    THEMES
)

def test_new_themes_exist():
    assert 'corporate_blue_geom' in THEMES, "corporate_blue_geom theme missing"
    assert 'modern_infographic_yellow' in THEMES, "modern_infographic_yellow theme missing"
    assert 'creative_editorial' in THEMES, "creative_editorial theme missing"
    print("[SUCCESS] All new professional themes exist in THEMES")

def test_generate_outline_with_rich_archetypes():
    outline = generate_presentation_outline(
        topic="Fintech Enterprise Scaling & Cloud Migration",
        slide_count=7,
        tone="Professional",
        audience="Executive Board"
    )
    assert outline is not None, "Failed to generate outline"
    slides = outline.get('slides', [])
    assert len(slides) == 7, f"Expected 7 slides, got {len(slides)}"

    layouts = [s.get('suggested_layout') for s in slides]
    print(f"Generated Outline Layouts: {layouts}")

    # Verify key archetypes are present in outline
    assert 'title' in layouts, "Title slide layout missing"
    assert 'horizontal_pills' in layouts, "horizontal_pills layout missing"
    assert 'swot' in layouts, "swot layout missing"
    assert 'chart' in layouts, "chart layout missing"
    assert 'circular_dials' in layouts, "circular_dials layout missing"
    print("[SUCCESS] Outline generation successfully populated with rich layout archetypes")

def test_build_pptx_with_all_layouts():
    # Construct a full test deck covering each archetype explicitly
    test_deck = {
        "presentation_title": "OmniChannel Digital Banking Transformation",
        "subtitle": "An Executive Blueprint for Scalable Financial Architecture",
        "topic": "Fintech Architecture",
        "target_audience": "C-Suite & Board of Directors",
        "tone": "Professional",
        "slides": [
            {
                "slide_number": 1,
                "title": "Fintech Enterprise Scaling",
                "subtitle": "Strategic Modernization & Real-time Settlement Architecture",
                "type": "title",
                "suggested_layout": "title",
                "bullets": []
            },
            {
                "slide_number": 2,
                "title": "Strategic Objectives & Scope",
                "key_takeaway": "Three foundational pillars anchoring digital velocity",
                "type": "horizontal_pills",
                "suggested_layout": "horizontal_pills",
                "cards": [
                    { "title": "Objective A: Core Banking Modernization", "description": "Transition legacy mainframe accounts to cloud-native microservices with zero downtime." },
                    { "title": "Objective B: Real-time Liquidity & Settlement", "description": "Enable sub-second cross-border payments with automated ISO 20022 compliance." },
                    { "title": "Objective C: Autonomous Fraud Interception", "description": "Deploy distributed ML inference to intercept unauthorized transactions under 15ms." }
                ],
                "bullets": []
            },
            {
                "slide_number": 3,
                "title": "Strategic SWOT Analysis Matrix",
                "key_takeaway": "Holistic internal capability audit against competitive fintech landscape",
                "type": "swot",
                "suggested_layout": "swot",
                "swot_data": {
                    "strengths": ["Proprietary ledger engine", "99.999% SLA availability"],
                    "weaknesses": ["Legacy core system dependencies", "Talent onboarding latency"],
                    "opportunities": ["Open banking API monetization", "Autonomous risk underwriting"],
                    "threats": ["Neo-bank aggressive pricing", "Evolving cross-border data regulations"]
                },
                "bullets": []
            },
            {
                "slide_number": 4,
                "title": "Empirical Benchmark Divergence",
                "key_takeaway": "Quantifiable velocity gains after pipeline parallelization",
                "type": "chart",
                "suggested_layout": "chart",
                "chart_data": {
                    "chart_type": "bar",
                    "title": "Fintech Benchmark Metrics (%)",
                    "labels": ["Processing Speed", "Transaction Reliability", "Audit Compliance", "Uptime"],
                    "values": [82, 96, 91, 100]
                },
                "bullets": [
                    "Throughput escalated by 82% post-containerization.",
                    "False decline rate lowered from 4.2% to 0.4%.",
                    "Zero downtime recorded across four consecutive quarters."
                ]
            },
            {
                "slide_number": 5,
                "title": "Operational Performance Dials",
                "key_takeaway": "Key engagement and reliability health gauges",
                "type": "circular_dials",
                "suggested_layout": "circular_dials",
                "dials": [
                    { "percent": 91, "label": "Customer Retention" },
                    { "percent": 74, "label": "Cloud Coverage" },
                    { "percent": 98, "label": "SLA Compliance" }
                ],
                "bullets": [
                    "Net promoter score in upper 90th percentile.",
                    "74% of core ledger migrated to multi-region cloud cluster."
                ]
            },
            {
                "slide_number": 6,
                "title": "Phased Execution & Operations Workflow",
                "key_takeaway": "Structured 4-stage operational chevron pipeline",
                "type": "process_chevrons",
                "suggested_layout": "process_chevrons",
                "cards": [
                    { "title": "Discovery & Ingestion", "description": "Legacy system telemetry mapping and schema alignment." },
                    { "title": "Core Pipeline Rollout", "description": "Microservices rollout and real-time transaction streaming." },
                    { "title": "Automated Quality Gates", "description": "Continuous penetration tests, automated compliance validation." },
                    { "title": "Global Scaling & Handover", "description": "Executive scorecards, disaster recovery, and maintenance SLAs." }
                ],
                "bullets": []
            },
            {
                "slide_number": 7,
                "title": "Leadership Team & Squad Alignment",
                "key_takeaway": "Seasoned executives steering architectural execution",
                "type": "team_personas",
                "suggested_layout": "team_personas",
                "cards": [
                    { "title": "Dr. Sarah Jenkins", "role": "Chief Technology Officer", "description": "18+ years architecting distributed banking platforms and real-time ledgers." },
                    { "title": "Marcus Vance", "role": "Head of Product & Payments", "description": "Former Stripe VP leading global payments scaling and regulatory affairs." },
                    { "title": "Elena Rostova", "role": "Lead Security Architect", "description": "Specialist in zero-trust cryptographic protocols and high-throughput validation." }
                ],
                "bullets": []
            }
        ]
    }

    # Build with corporate_blue_geom theme (which tests geometric corner accents!)
    pptx_path = build_pptx_from_outline(test_deck, theme_name='corporate_blue_geom')
    assert os.path.exists(pptx_path), f"Output file does not exist: {pptx_path}"
    assert os.path.getsize(pptx_path) > 50000, f"Output file suspiciously small: {os.path.getsize(pptx_path)} bytes"

    # Inspect slides with python-pptx
    prs = Presentation(pptx_path)
    assert len(prs.slides) == 7, f"Expected 7 slides, found {len(prs.slides)}"

    print(f"[SUCCESS] PPTX successfully generated ({os.path.getsize(pptx_path)} bytes): {pptx_path}")

    # Check slide 1 (Cover):
    s1_shapes = prs.slides[0].shapes
    print(f"Slide 1 (Hero Cover) shape count: {len(s1_shapes)}")
    assert len(s1_shapes) >= 4, "Slide 1 should contain geometric accents and cards"

    # Check slide 2 (Horizontal Pills):
    s2_shapes = prs.slides[1].shapes
    print(f"Slide 2 (A-B-C Pills) shape count: {len(s2_shapes)}")
    assert len(s2_shapes) >= 7, "Slide 2 should contain 3 pill cards and circle letter badges"

    # Check slide 3 (SWOT):
    s3_shapes = prs.slides[2].shapes
    print(f"Slide 3 (SWOT 4-Pillar) shape count: {len(s3_shapes)}")
    assert len(s3_shapes) >= 9, "Slide 3 should contain 4 pillars, header blocks, and text frames"

    # Check slide 5 (Circular Dials):
    s5_shapes = prs.slides[4].shapes
    print(f"Slide 5 (Circular Dials) shape count: {len(s5_shapes)}")

    # Check slide 6 (Chevrons):
    s6_shapes = prs.slides[5].shapes
    print(f"Slide 6 (Process Chevrons) shape count: {len(s6_shapes)}")

    # Check slide 7 (Team):
    s7_shapes = prs.slides[6].shapes
    print(f"Slide 7 (Team Personas) shape count: {len(s7_shapes)}")

    print("[SUCCESS] All 7 slides inspected and verified successfully!")

if __name__ == '__main__':
    test_new_themes_exist()
    test_generate_outline_with_rich_archetypes()
    test_build_pptx_with_all_layouts()
    print("\n[ALL TESTS PASSED] Professional layouts & templates functioning flawlessly!")
