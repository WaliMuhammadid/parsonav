import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_styled_table(doc, headers, data, col_widths=None):
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1F2937") # Dark gray/slate
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=160, right=160)
        p = hdr_cells[i].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        p.runs[0].font.size = Pt(9.5)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # Data Rows
    for row_idx, row_data in enumerate(data):
        row_cells = table.rows[row_idx + 1].cells
        bg_color = "F9FAFB" if row_idx % 2 == 0 else "FFFFFF"
        for col_idx, cell_value in enumerate(row_data):
            row_cells[col_idx].text = str(cell_value)
            set_cell_background(row_cells[col_idx], bg_color)
            set_cell_margins(row_cells[col_idx], top=100, bottom=100, left=140, right=140)
            p = row_cells[col_idx].paragraphs[0]
            if len(p.runs) > 0:
                p.runs[0].font.size = Pt(9)
                p.runs[0].font.color.rgb = RGBColor(31, 41, 55)

    # Set Column Widths if provided
    if col_widths:
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = Inches(width)

    doc.add_paragraph() # Spacing
    return table

def enhance_docx(input_path, output_path):
    print(f"Reading {input_path}...")
    orig_doc = docx.Document(input_path)
    
    # We will build a comprehensive, beautifully structured document
    doc = docx.Document()

    # Title & Metadata
    title_p = doc.add_paragraph()
    title_run = title_p.add_run("Gamma.app: Feature, Workflow & UI Analysis")
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(79, 70, 229) # Indigo
    title_p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run("A Reference Study & Implementation Blueprint for Upgrading the Presenova AI Presentation Generator Module\n(Expanded & Enhanced Technical Edition)")
    sub_run.font.size = Pt(13)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(107, 114, 128)

    # Meta box
    meta_p = doc.add_paragraph()
    meta_p.add_run("Prepared for: ").bold = True
    meta_p.add_run("Presenova — Final Year Project (AI Presentation Platform)\n")
    meta_p.add_run("Subject Tool Analyzed: ").bold = True
    meta_p.add_run("Gamma.app (gamma.app)\n")
    meta_p.add_run("Document Type: ").bold = True
    meta_p.add_run("Competitive Feature Teardown, Asymmetric Moat Analysis & Integration Specification\n")
    meta_p.add_run("Release Target: ").bold = True
    meta_p.add_run("Presenova v1.2.0 Upgrade Roadmap\n")
    meta_p.add_run("Date: ").bold = True
    meta_p.add_run("September 2026 (Audited & Updated)")

    doc.add_paragraph("―" * 45).alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Table of Contents
    h_toc = doc.add_heading("Table of Contents", level=1)
    toc_items = [
        "1. Executive Summary",
        "2. What Is Gamma.app",
        "   2.1 Positioning vs. Traditional Slide Software",
        "3. Core Feature Set",
        "   3.1 Multi-Format Input Ingestion",
        "   3.2 AI Outline Stage (Pre-Generation Checkpoint)",
        "   3.3 Card-Based Content Model & Smart Formatting",
        "   3.4 Theme Engine (Design/Content Separation)",
        "   3.5 Conversational AI Agent (In-Context Editing)",
        "   3.6 Media Generation & Curation",
        "   3.7 Page/Deck-Level Settings",
        "   3.8 Collaboration & Sharing",
        "   3.9 Connectors & Automation",
        "4. End-to-End User Workflow",
        "5. User Interface Architecture",
        "6. Feature Mapping: Gamma.app → Presenova AI Presentation Generator",
        "   6.1 What Should Not Be Copied Directly",
        "   6.2 Presenova's Asymmetric Competitive Moats Over Gamma.app",
        "   6.3 Smart Semantic Layout Engine (Content-Shape Classification via spaCy)",
        "   6.4 Technical API Specifications for the Upgraded Generator Module",
        "   6.5 Frontend UI/UX Architecture Blueprint (4-Stage Generation Wizard)",
        "7. Recommended Implementation Roadmap & Sprint Deliverables",
        "8. Conclusion & Future Outlook"
    ]
    for item in toc_items:
        p = doc.add_paragraph(item, style='List Paragraph')
        p.paragraph_format.space_after = Pt(2)

    doc.add_paragraph()

    # Chapter 1: Executive Summary
    doc.add_heading("1. Executive Summary", level=1)
    doc.add_paragraph(
        "Gamma.app is a cloud-based, AI-first content generation platform that produces presentations, documents, "
        "and interactive content from a prompt, an outline, or an imported file. Its primary differentiator versus "
        "traditional slide software (such as Microsoft PowerPoint or Google Slides) is that it treats a presentation as "
        "a sequence of fluid, flexible 'cards' rather than rigid, fixed-dimension 16:9 slides, separates underlying content "
        "from visual styling through an immutable global Theme system, and layers an in-context conversational agent for "
        "iterative natural-language adjustments."
    )
    doc.add_paragraph(
        "This research report provides a deep-dive competitive teardown of Gamma's architecture, user flows, and UX patterns, "
        "and systematically maps each capability to Presenova's AI Presentation Generator (Module 7). Presenova currently utilizes "
        "a local-first, privacy-preserving stack consisting of python-pptx, spaCy dependency analysis, and deterministic layout "
        "synthesis across four preset themes (Modern Dark, Corporate Clean, Creative Neon, Academic Gold). By adopting Gamma's "
        "highest-leverage architectural innovations—specifically content/theme decoupling, pre-generation outline review, "
        "and smart content-shaped layouts—while vigorously maintaining Presenova's core moats in real-time vision telemetry, "
        "vocal coaching, academic viva defense generation, and zero-cloud privacy, Presenova can deliver a best-in-class "
        "academic and executive presentation platform."
    )

    # Chapter 2: What Is Gamma.app
    doc.add_heading("2. What Is Gamma.app", level=1)
    doc.add_paragraph(
        "Gamma is a browser-based application that synthesizes text prompts, pasted outlines, or uploaded documents into "
        "cohesive, styled presentation decks in seconds. It bridges the gap between document editors (like Notion or Google Docs) "
        "and presentation software (PowerPoint). Content exists in reflowable cards that dynamically expand to eliminate text "
        "clipping, while global styling rules ensure visual consistency without requiring manual slide design."
    )
    
    doc.add_heading("2.1 Positioning vs. Traditional Slide Software", level=2)
    doc.add_paragraph(
        "The following matrix contrasts traditional PowerPoint and Presenova's current v1.1 generator against the Gamma.app paradigm:"
    )

    t0_headers = ["Dimensional Aspect", "Traditional PowerPoint / Presenova v1.1", "Gamma.app Paradigm"]
    t0_data = [
        ["Content Unit", "Fixed-size 16:9 canvas; manual overflow handling", "Flexible 'card' that reflows automatically to content volume"],
        ["Design Control", "Manual coordinate placement of text boxes & shapes", "Autonomous AI layout engine governed by global theme; editable"],
        ["Styling Architecture", "Per-slide or per-master slide formatting", "Global Theme Engine completely decoupled from underlying text"],
        ["Editing Method", "Manual point-and-click GUI editing", "Natural language chat agent + inline block manipulation"],
        ["Input Ingestion", "Blank canvas or template selection", "Natural language prompt, pasted text, PDF/DOCX/PPTX import, URL"],
        ["Output Formats", "PPTX (and exported PDF)", "Dynamic Web Link, PPTX, PDF, Google Slides, PNG"],
        ["Domain Focus", "Slide authoring only", "Card-based authoring and web sharing"],
        ["Live Rehearsal & Delivery", "None (manual presenter notes only)", "None (Gamma focuses exclusively on content creation)"]
    ]
    add_styled_table(doc, t0_headers, t0_data, [1.5, 2.5, 2.5])

    # Chapter 3: Core Feature Set
    doc.add_heading("3. Core Feature Set", level=1)

    doc.add_heading("3.1 Multi-Format Input Ingestion", level=2)
    doc.add_paragraph(
        "Gamma accepts three distinct input modalities at session initiation:\n"
        "1. Generate from Prompt: A high-level description specifying topic, audience, tone, and slide count.\n"
        "2. Paste in Text: Pre-drafted outlines, lecture notes, or rough manuscripts parsed into structured cards.\n"
        "3. Import File / URL: Existing PPTX, PDF, Word documents, or web URLs scraped and parsed directly into cards.\n\n"
        "Presenova Opportunity: Presenova already possesses robust, multi-format extraction utilities in `services/text_extractor.py` "
        "(developed for the Document Analyzer module). Exposing an 'Import & Transform' endpoint in the Presentation Generator "
        "allows users to convert existing PDF reports or legacy slides into brand-new styled decks with zero new dependency overhead."
    )

    doc.add_heading("3.2 AI Outline Stage (Pre-Generation Checkpoint)", level=2)
    doc.add_paragraph(
        "A critical UX safeguard in Gamma is the Outline Stage. Before visual cards are constructed, the system generates "
        "a lightweight, editable outline showing proposed card titles and sub-bullets. Users can reorder, delete, merge, or add "
        "points. Rendering occurs only upon user confirmation. This eliminates computational waste and gives users structural "
        "mastery over the narrative flow."
    )

    doc.add_heading("3.3 Card-Based Content Model & Smart Formatting", level=2)
    doc.add_paragraph(
        "Gamma discards rigid slide frames in favor of flexible cards. Key layout features include:\n"
        "• Adaptive Column Grids: Dynamic multi-column blocks (up to 6 columns) for side-by-side feature comparisons.\n"
        "• Smart Content-Shaped Formatting: The engine inspects semantic structure: numerical items render as KPI Stat Callouts, "
        "sequential steps render as Timeline Process Flows, and contrastive points render as Comparison Tables.\n"
        "• Card Header & Footer Slots: Precise placements for slide numbers, category breadcrumbs, logos, and confidentiality markers."
    )

    doc.add_heading("3.4 Theme Engine (Design/Content Separation)", level=2)
    doc.add_paragraph(
        "Gamma strictly enforces the separation of content and presentation. Themes are defined by JSON-like visual manifests containing:\n"
        "• Color Palettes: Background, surface, primary text, secondary text, accents, and borders.\n"
        "• Typography Pairings: Complementary header and body font selections with controlled kerning and line heights.\n"
        "• Card Geometry: Corner radii, card elevation shadows, and border stroke weights.\n"
        "Switching a theme transforms the visual rendering of the entire deck in real time without mutating any text or data."
    )

    doc.add_heading("3.5 Conversational AI Agent (In-Context Editing)", level=2)
    doc.add_paragraph(
        "Gamma includes a persistent slide assistant that accepts scoped prompts: 'Make card 3 more concise,' 'Convert bullets into "
        "a three-column grid,' or 'Add a slide addressing competitive risks.' In Presenova, where an external LLM is strictly "
        "prohibited, this capability is mirrored via a deterministic, local TF-IDF + LogisticRegression Command Palette "
        "(reusing the Phase 5 Coach Intent Engine)."
    )

    doc.add_heading("3.6 Media Generation & Curation", level=2)
    doc.add_paragraph(
        "Gamma provides text-to-image synthesis (Gamma Imagine) and automated stock photo curation. For Presenova's offline "
        "academic footprint, generative diffusion models are replaced by programmatic Python data visualizations (matplotlib charts), "
        "vector shapes, and high-resolution academic diagram templates."
    )

    doc.add_heading("3.7 Page/Deck-Level Settings", level=2)
    doc.add_paragraph(
        "Gamma provides granular controls over card aspect ratios (Fluid vs. Standard 16:9), backdrop visibility, and print margins."
    )

    doc.add_heading("3.8 Collaboration & Sharing", level=2)
    doc.add_paragraph(
        "Features real-time collaborative editing, public web links, view-only modes, and universal exports (PPTX, PDF, PNG)."
    )

    doc.add_heading("3.9 Connectors & Automation", level=2)
    doc.add_paragraph(
        "Gamma exposes webhooks and third-party connector hooks for Zapier, Make, and Claude. Presenova can expose its generator "
        "endpoints as standardized REST APIs for batch academic deck production."
    )

    # Chapter 4: End-to-End User Workflow
    doc.add_heading("4. End-to-End User Workflow", level=1)
    doc.add_paragraph(
        "Gamma's user journey follows five strictly sequenced stages. Below is the workflow analysis mapped against system mechanics:"
    )

    t1_headers = ["Stage", "User Interaction", "Underlying System Mechanism", "Presenova Adaptation"]
    t1_data = [
        ["1. Input Seed", "Enters topic prompt, pastes text, or uploads document", "Parses raw input into structured entities & topic context", "Reuses services/text_extractor.py to parse PDF/DOCX/PPTX into clean text"],
        ["2. Outline Review", "Inspects, reorders, edits, or adds card titles", "Holds state in mutable JSON model; no rendering cost incurred", "New endpoint /api/presentation-generator/outline returning editable outline"],
        ["3. Theme Selection", "Chooses preset theme or custom visual palette", "Binds theme tokens (hex colors, fonts, margins) to model", "Selects among Presenova themes or custom user-defined JSON theme schema"],
        ["4. Card Synthesis", "Clicks 'Generate Presentation'", "Executes layout classification and constructs card geometries", "python-pptx layout engine builds styled 16:9 slides with 6x6 bullet rules"],
        ["5. Refine & Export", "Performs manual edits or executes command edits; downloads", "Applies scoped transforms; compiles PPTX / PDF binary", "Delivers downloadable .pptx file, PDF export, and one-click handoff to Live Coach"]
    ]
    add_styled_table(doc, t1_headers, t1_data, [1.1, 1.8, 1.8, 1.8])

    # Chapter 5: User Interface Architecture
    doc.add_heading("5. User Interface Architecture", level=1)
    doc.add_paragraph(
        "Gamma's UI relies on four foundational architectural principles:\n"
        "1. Progressive Disclosure: Complex styling controls are hidden during input; only relevant knobs appear at each stage.\n"
        "2. Vertical Continuous Canvas: Decks scroll vertically like documents, allowing natural multi-slide reading.\n"
        "3. Floating Contextual Controls: Hovering over a card reveals quick-action toolbars (layout switcher, card color, delete).\n"
        "4. Non-Destructive Global Theme Engine: Theme changes restyle visual tokens without touching underlying content strings."
    )

    # Chapter 6: Feature Mapping & Presenova Enhancements
    doc.add_heading("6. Feature Mapping: Gamma.app → Presenova AI Presentation Generator", level=1)
    doc.add_paragraph(
        "The following matrix outlines the strategic mapping of Gamma features to Presenova's Module 7 generator:"
    )

    t2_headers = ["Gamma Capability", "Presenova Today (v1.1)", "Proposed Presenova Upgrade", "Feasibility & Stack"]
    t2_data = [
        ["Pre-Generation Outline Checkpoint", "One-pass generation; no outline review", "Add /outline endpoint; user confirms titles before PPTX build", "High (spaCy outline logic already exists)"],
        ["Smart Content-Shaped Layouts", "Uniform bullet card layout across slides", "Content-shape classifier choosing Stat, Timeline, or Comparison", "High (spaCy entity + numerical token rules)"],
        ["Global Theme Customizer", "4 hardcoded themes in Python code", "User-definable JSON theme schema with hex/font overrides", "High (decouple themes into config dictionary)"],
        ["Multi-Column Comparison Grids", "Single column bullet lists only", "2-column and 3-column visual card layouts in python-pptx", "Medium (requires python-pptx coordinate math)"],
        ["Import Existing File as Seed", "Text prompt only", "Accept .pptx, .pdf, .docx uploads and feed text into outline stage", "High (reuses services/text_extractor.py)"],
        ["Multi-Format Export (PDF + PPTX)", "PPTX export only", "Client-side PDF generation via jsPDF or backend conversion", "High (jspdf already installed in frontend)"],
        ["Slide Headers, Footers & Branding", "Title and body only", "Add configurable slide numbers, category tags, and logos", "High (python-pptx shape placement)"],
        ["Conversational Edit Agent", "Full regeneration required for any change", "Local intent command palette ('shorten slide', 'change theme')", "Medium (TF-IDF + LogisticRegression pipeline)"]
    ]
    add_styled_table(doc, t2_headers, t2_data, [1.4, 1.6, 2.0, 1.5])

    doc.add_heading("6.1 What Should Not Be Copied Directly", level=2)
    doc.add_paragraph(
        "• Continuous Cloud Dependency: Gamma requires cloud connectivity. Presenova must remain 100% operational offline.\n"
        "• Third-Party LLM Agent APIs: Gamma relies on OpenAI/Anthropic APIs. Presenova adheres to its local ML/spaCy architecture mandate.\n"
        "• Heavy Generative Diffusion Models: Gamma Imagine requires massive GPU infrastructure. Presenova substitutes clean programmatic diagrams and charts."
    )

    # NEW SECTION 6.2: Presenova's Asymmetric Competitive Moats
    doc.add_heading("6.2 Presenova's Asymmetric Competitive Moats Over Gamma.app", level=2)
    doc.add_paragraph(
        "While Gamma.app excels in slide authoring, Presenova possesses profound competitive advantages that Gamma does not even attempt "
        "to address. Gamma is solely a document/presentation creation tool; Presenova is an integrated presentation preparation, "
        "multi-modal analysis, and live delivery coaching ecosystem. The following capabilities establish Presenova's distinct moats:"
    )
    doc.add_paragraph(
        "1. Computer Vision Rehearsal Telemetry (MediaPipe Face Mesh):\n"
        "Presenova tracks 478 facial landmarks (468 base + 10 iris refinement points, indices 468–477). It computes Eye Contact "
        "ratios using iris displacement, monitors blink frequency via Eye Aspect Ratio (EAR < 0.16), and tracks head posture yaw/pitch "
        "deviations in real time over WebSockets. Gamma has no vision or webcam integration."
    )
    doc.add_paragraph(
        "2. Vocal Dynamics & Speech Disfluency Tracking (Groq Whisper):\n"
        "Presenova streams 3-second audio buffers, computes instantaneous Words-Per-Minute (WPM), detects filler words ('um', 'uh', "
        "'like', 'you know'), logs consecutive word repetitions, and conducts LanguageTool grammar audits. Gamma contains zero audio tools."
    )
    doc.add_paragraph(
        "3. Academic Viva & Thesis Defense Question Generator (FAISS Vector RAG):\n"
        "Presenova chunks research documents into 200-word passages, embeds them with SentenceTransformer ('all-MiniLM-L6-v2'), "
        "indexes them in a FAISS vector database, and generates categorized defense questions (Basic, Intermediate, Advanced) to prepare "
        "students for hostile panel cross-examinations. Gamma lacks any academic defense preparation capability."
    )
    doc.add_paragraph(
        "4. Quantitative 7 Cs Communication Evaluation Framework:\n"
        "Presenova scores presentations across 7 core communication pillars (Clarity, Conciseness, Completeness, Concreteness, "
        "Consideration, Correctness, Courtesy) alongside 10 diagnostic category breakdown scores, supported by 7 deterministic sub-analyzers."
    )
    doc.add_paragraph(
        "5. Local-First Classical ML & Complete Data Privacy:\n"
        "All classification, NLP scoring, and semantic consistency checking run locally via scikit-learn, spaCy, and FAISS. Sensitive "
        "corporate decks and unpublished academic research never leave the user's host machine."
    )

    # Comparison Table
    moat_headers = ["Capability / Feature", "Presenova AI Presentation Platform", "Gamma.app", "Microsoft PowerPoint / Copilot"]
    moat_data = [
        ["AI Deck Generation from Prompt", "Yes (python-pptx + spaCy structured cards)", "Yes (AI Card Generator)", "Yes (Copilot prompt generation)"],
        ["Real-Time Webcam Eye Tracking", "Yes (MediaPipe Iris tracking, 478 landmarks)", "No", "No"],
        ["Head Posture & Slouch Detection", "Yes (Nose landmark 1 & symmetry heuristics)", "No", "No"],
        ["Speech Pacing & WPM Telemetry", "Yes (Groq Whisper STT + pacing gauge)", "No", "Basic (Speaker Coach pace only)"],
        ["Filler Word & Repetition Analysis", "Yes (Exact filler counts & percentage)", "No", "Basic (Generic filler summary)"],
        ["Academic Viva Defense RAG Engine", "Yes (FAISS + SentenceTransformers RAG)", "No", "No"],
        ["7 Cs Communication Framework", "Yes (Deterministic multi-trait evaluation)", "No", "No"],
        ["Slide Rewrite (6x6 Rule Enforcement)", "Yes (spaCy dependency passive-to-active)", "Manual chat edits", "Basic grammar suggestions"],
        ["Privacy / Offline Capability", "100% Local / Self-Hosted Compatible", "Cloud-only (data sent to servers)", "Cloud-only (requires M365 cloud)"]
    ]
    add_styled_table(doc, moat_headers, moat_data, [1.6, 2.0, 1.5, 1.5])

    # NEW SECTION 6.3: Smart Semantic Layout Engine
    doc.add_heading("6.3 Smart Semantic Layout Engine (Content-Shape Classification via spaCy)", level=2)
    doc.add_paragraph(
        "To emulate Gamma's smart card layouts within Presenova's local-first architecture, `services/presentation_generator.py` "
        "can be augmented with a deterministic content-shape classifier. By analyzing numerical tokens, entity types, and sentence "
        "dependencies, the generator selects the optimal visual slide archetype:"
    )
    doc.add_paragraph(
        "• Archetype 1: Stat Callout Card — Selected when a bullet contains percentage values, currency markers, or standalone "
        "cardinal numbers (e.g., '85% increase in efficiency', '$4.2M budget allocation'). Renders oversized highlight text with a small descriptive label.\n"
        "• Archetype 2: Multi-Column Comparison Grid — Selected when bullets contain comparative conjunctions ('vs', 'compared to', "
        "'whereas', 'pros and cons'). Renders 2 or 3 distinct vertical card containers side-by-side.\n"
        "• Archetype 3: Sequential Process / Timeline — Selected when headings or bullets indicate sequential phases ('Step 1', "
        "'Phase I', 'Initialization -> Training -> Evaluation'). Renders connected horizontal chevron cards.\n"
        "• Archetype 4: Standard 6x6 Bullet Card — The default structured slide archetype, enforcing a maximum of 6 bullets with "
        "under 15 words per bullet point."
    )

    doc.add_paragraph("Reference Python Implementation for Content-Shape Classifier:")
    code_text = (
        "def classify_slide_intent_spacy(title: str, bullets: list[str]) -> str:\n"
        "    \"\"\"\n"
        "    Deterministically classifies slide content to choose the optimal python-pptx visual layout.\n"
        "    Returns: 'stat_callout' | 'comparison_grid' | 'process_timeline' | 'standard_bullet'\n"
        "    \"\"\"\n"
        "    doc = nlp(' '.join([title] + bullets))\n"
        "    num_entities = [ent for ent in doc.ents if ent.label_ in ('CARDINAL', 'PERCENT', 'MONEY')]\n"
        "    text_lower = (title + ' ' + ' '.join(bullets)).lower()\n"
        "    \n"
        "    # Rule 1: High numerical density triggers Stat Callout\n"
        "    if len(num_entities) >= 2 and any(char in text_lower for char in ['%', '$', 'kpi', 'rate']):\n"
        "        return 'stat_callout'\n"
        "    \n"
        "    # Rule 2: Contrastive markers trigger Comparison Grid\n"
        "    if any(k in text_lower for k in [' vs ', 'versus', 'compared to', 'pros and cons', 'advantages and']):\n"
        "        return 'comparison_grid'\n"
        "    \n"
        "    # Rule 3: Process/Phase markers trigger Timeline\n"
        "    if any(k in text_lower for k in ['step 1', 'phase 1', 'stage 1', 'pipeline', 'workflow', 'roadmap']):\n"
        "        return 'process_timeline'\n"
        "    \n"
        "    return 'standard_bullet'\n"
    )
    p_code = doc.add_paragraph(code_text)
    p_code.runs[0].font.name = 'Consolas'
    p_code.runs[0].font.size = Pt(8.5)
    p_code.paragraph_format.left_indent = Inches(0.2)

    # NEW SECTION 6.4: Technical API Specifications
    doc.add_heading("6.4 Technical API Specifications for the Upgraded Generator Module", level=2)
    doc.add_paragraph(
        "To implement the two-stage Gamma generation pipeline, the existing `/api/presentation-generator` blueprint is "
        "extended with the following modular REST endpoints:"
    )
    
    doc.add_paragraph("1. POST /api/presentation-generator/outline\nGenerates an editable outline structure without rendering visual slides.")
    api1_text = (
        "Request Payload:\n"
        "{\n"
        '  "topic": "Autonomous Driving Systems",\n'
        '  "slide_count": 6,\n'
        '  "tone": "Academic",\n'
        '  "target_audience": "Engineering Faculty"\n'
        "}\n\n"
        "Response (200 OK):\n"
        "{\n"
        '  "success": true,\n'
        '  "outline_id": "out_9a8b7c6d5e",\n'
        '  "topic": "Autonomous Driving Systems",\n'
        '  "sections": [\n'
        '    { "slide_number": 1, "title": "Introduction to Autonomous Driving", "suggested_layout": "standard_bullet", "key_points": ["Evolution from ADAS to Level 5 autonomy", "Core sensor modalities: LiDAR, Radar, Cameras"] },\n'
        '    { "slide_number": 2, "title": "Perception Pipeline & Deep Learning", "suggested_layout": "process_timeline", "key_points": ["Raw Sensor Data Acquisition", "3D Bounding Box Object Detection", "Temporal Kalman Filter Tracking"] },\n'
        '    { "slide_number": 3, "title": "LiDAR vs. Vision-Only Architecture", "suggested_layout": "comparison_grid", "key_points": ["LiDAR: Direct depth accuracy, high hardware cost", "Vision: Photometric richness, edge compute challenges"] },\n'
        '    { "slide_number": 4, "title": "System Latency & Safety Metrics", "suggested_layout": "stat_callout", "key_points": ["99.999% Collision avoidance reliability", "Under 15ms inference latency per frame"] }\n'
        "  ]\n"
        "}\n"
    )
    p_api1 = doc.add_paragraph(api1_text)
    p_api1.runs[0].font.name = 'Consolas'
    p_api1.runs[0].font.size = Pt(8.5)
    p_api1.paragraph_format.left_indent = Inches(0.2)

    doc.add_paragraph("2. POST /api/presentation-generator/generate-from-outline\nAccepts the user-confirmed outline and custom theme settings to build the final PowerPoint presentation.")
    api2_text = (
        "Request Payload:\n"
        "{\n"
        '  "outline_id": "out_9a8b7c6d5e",\n'
        '  "theme": "academic_gold",\n'
        '  "custom_overrides": {\n'
        '    "header_footer": { "show_page_numbers": true, "confidentiality_text": "FYP Final Defense 2026" },\n'
        '    "primary_color": "#D97706"\n'
        "  },\n"
        '  "confirmed_sections": [ ... modified section objects ... ]\n'
        "}\n\n"
        "Response (200 OK):\n"
        "{\n"
        '  "success": true,\n'
        '  "filename": "Presenova_Autonomous_Driving_Systems_2026.pptx",\n'
        '  "download_url": "/api/presentation-generator/download/Presenova_Autonomous_Driving_Systems_2026.pptx",\n'
        '  "slide_count": 6,\n'
        '  "theme_applied": "academic_gold"\n'
        "}\n"
    )
    p_api2 = doc.add_paragraph(api2_text)
    p_api2.runs[0].font.name = 'Consolas'
    p_api2.runs[0].font.size = Pt(8.5)
    p_api2.paragraph_format.left_indent = Inches(0.2)

    doc.add_paragraph("3. POST /api/presentation-generator/import-seed\nAccepts a multipart file upload (.pdf, .docx, .pptx), extracts text via `services/text_extractor.py`, and returns an editable outline.")

    # NEW SECTION 6.5: Frontend UI/UX Architecture Blueprint
    doc.add_heading("6.5 Frontend UI/UX Architecture Blueprint (4-Stage Generation Wizard)", level=2)
    doc.add_paragraph(
        "To deliver a sleek, Gamma-grade authoring experience in the React 18 / TypeScript frontend (`frontend/src/pages/PresentationGenerator.tsx`), "
        "the interface is restructured into a progressive 4-step wizard:"
    )
    doc.add_paragraph(
        "• Step 1: Input Ingestion Hub\n"
        "Tabs for 'Topic Prompt' and 'Upload Document Seed'. Users configure tone, audience, and requested slide count with visual pill selectors.\n\n"
        "• Step 2: Interactive Outline Canvas\n"
        "A drag-and-drop vertical card list. Users can reorder sections, edit titles, add new section cards with a '+' button, and select "
        "the visual layout archetype (Bullet, Stat, Comparison, Timeline) via an inline dropdown.\n\n"
        "• Step 3: Theme & Branding Studio\n"
        "Card previews rendered live in CSS using Presenova's theme tokens. Users preview color swatches (Modern Dark, Corporate Clean, "
        "Creative Neon, Academic Gold, or Custom) and toggle slide number/footer visibility.\n\n"
        "• Step 4: Deck Download & Delivery Handoff\n"
        "Displays generation success, one-click PPTX and PDF download buttons, and immediate action triggers: 'Launch Live Practice Rehearsal' "
        "(navigating directly to `LiveCoach.tsx`) and 'Generate Academic Viva Defense Questions' (navigating to `question_generator`)."
    )

    # Chapter 7: Recommended Implementation Roadmap
    doc.add_heading("7. Recommended Implementation Roadmap & Sprint Deliverables", level=1)
    doc.add_paragraph(
        "The upgrade roadmap is divided into three actionable development sprints:"
    )

    sprint_headers = ["Sprint & Phase", "Key Deliverables", "Target Files", "Verification & Test Suite"]
    sprint_data = [
        ["Sprint 1\n(Weeks 1–2)\nQuick Wins", "1. Two-Stage Outline Checkpoint\n2. Direct PDF Export via jsPDF\n3. Header/Footer/Page-Number slots in python-pptx", "routes/presentation_generator.py\nservices/presentation_generator.py\nfrontend/src/pages/PresentationGenerator.tsx", "test_presentation_generator.py\nVerify outline JSON & PPTX slide number XML shapes"],
        ["Sprint 2\n(Weeks 3–4)\nSmart Layouts", "1. Content-Shape Classifier (spaCy)\n2. 2-Column Comparison Layout\n3. Stat Callout Layout\n4. Import Seed (.pdf/.docx) route", "services/presentation_generator.py\nservices/text_extractor.py\nfrontend/src/components/FileUploader.tsx", "test_semantic_layouts.py\nVerify KPI numbers trigger stat cards and 'vs' triggers 2-column grid"],
        ["Sprint 3\n(Weeks 5–6)\nAdvanced Suite", "1. Custom JSON Theme Studio\n2. Local TF-IDF Command Palette ('shorten slide', 'restyle')\n3. One-Click Handoff to Live Coach & Viva RAG", "services/coach_intent_engine.py\nfrontend/src/pages/PresentationGenerator.tsx\nfrontend/src/pages/LiveCoach.tsx", "test_generator_intent.py\nEnd-to-end integration test from prompt to live rehearsal scorecard"]
    ]
    add_styled_table(doc, sprint_headers, sprint_data, [1.4, 2.2, 2.0, 1.6])

    # Chapter 8: Conclusion
    doc.add_heading("8. Conclusion & Future Outlook", level=1)
    doc.add_paragraph(
        "Gamma.app's core breakthrough is fundamentally structural rather than algorithmic: decoupling visual design from raw content "
        "via a global theme object, checkpointing narrative outlines prior to rendering, and adapting layout geometry dynamically to "
        "content density. These architectural concepts can be implemented directly into Presenova's existing python-pptx and spaCy "
        "engine without introducing cloud vendor dependencies or violating the offline classical ML mandate."
    )
    doc.add_paragraph(
        "By fusing Gamma's streamlined card-authoring paradigm with Presenova's unrivaled, proprietary moats—real-time MediaPipe iris "
        "tracking, Groq Whisper vocal dynamics, FAISS academic viva defense cross-examination, and 7 Cs communication scoring—Presenova "
        "transcends simple slide creation. It emerges as the industry's most comprehensive, privacy-preserving presentation intelligence "
        "and executive rehearsal platform."
    )

    print(f"Saving enhanced document to {output_path}...")
    doc.save(output_path)
    print("Document saved successfully!")

if __name__ == "__main__":
    src = "Gamma_Feature_Analysis_Presenova.docx"
    dst = "Gamma_Feature_Analysis_Presenova.docx"
    enhance_docx(src, dst)
