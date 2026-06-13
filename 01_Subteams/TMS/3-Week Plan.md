# TMS Project Plan

## Goals Overview

| Goal | Measurables | Deliverables |
|------|-------------|--------------|
| **Finish CAD for Chassis** | Completion of frame; plan for 3D printing so striations are strong and won't result in cracking; verify PLA is insoluble; more possible fluid tests in water | Completed assembly in GitHub; bill and plan for filament; assembly spliced and ready for 3D printing; tapered washers CADed |
| **Float** | Collaboration and deliberate new design options for float; create solution for internal ballast system; design pressure release | New design incorporating internal ballast system (needs F&P collaboration); fully designed pressure release |
| **Claw Improvements** | Complete deliberation about claw design and whether changes or improvements are wanted | Final idea or improvement implemented |

---

## Team Members

| Name | Skills | Training Focus |
|------|--------|----------------|
| Alexandria Llavona | SolidWorks, Manufacturing | Leading sub-team to create a functional ROV |
| Matthew | CAD and prototyping | TBD |
| Ryann | CAD and stress work | TBD (CAD, stress testing) |
| Elif | CAD and manufacturing | TBD |

---

## Software & Tools

| Software/Tool | Purpose | Members | Resources/Links |
|---------------|---------|---------|-----------------|
| SolidWorks | 3D Modeling | All Members | — |
| Fab Lab / RPS / FEDC | Constructing and printing ROV | TBD | — |

---

## Training Plan

> **Action Required:** Get your [Red Badge](https://fedc.tamu.edu/) — sign up on the FEDC website as soon as possible!

Team members will use the Red Badge to access fabrication equipment, get familiar with SolidWorks, and build skills in CADing, printing, and assembling the final product.

---

## Documentation: Known Issues & Fixes

### Chassis

- **CAD:** Thicken lower and upper enclosure so heated inserts don't pop through
- **Striation Cracks**
  - *Long-term fix:* Print chassis parts long-ways (cracks form along striations)
  - *Short-term fix:* Heat gun set to 305°C, heat until plastic melts together
- Ballast system is currently external — needs to be internal
- Limit holes on the float; use multiple waterproofing methods

### Claw Parts

- Wrist joint is good; holes in claw joint need remodeling (too close to edge)
- Thicken middle section due to heated inserts sticking through
- **Use heated inserts** — much better than tapping
- If a heated insert starts to twist:
  1. Leave the target screw in the hole while inserting
  2. If stripped: heat soldering iron, remove it, use a 3D pin to fill the hole, redrill, and place a new heated insert
- If a screw won't pass through the insert, there is likely plastic in the threads:
  - Pick out the threads (time-consuming), or repeat the insert replacement process
- Double the waterproofing on the float (e.g., o-rings + epoxy coating)

### Brackets

- Need to be bigger — current brackets are too thin and flex too easily
- Any metal on the claw should use the thicker metal stock purchased this semester
- **Hole alignment issues:** Drill bracket holes larger if needed, but best practice is to drill all holes first, place heated inserts, confirm screws seat, then measure distances with calipers

### General

- Improve naming conventions
- Use zip files for sharing assemblies

---

## Timeline

### Summer — 3-Week Sprint

| Date | Task |
|------|------|
| June 8–10 | Requirements complete |
| Week 1–2 | Get changes made to the chassis; deliberate float changes (integrate internal ballast); save all new chassis versions to [GitHub](https://github.com/3lover/TAMU-MateROV) |
| Week 2–3 | Discuss and implement claw modifications; complete Red Badge training |

### Fall Semester

- After first PDR: begin 3D printing PLA chassis parts before the print rush
- Print new brackets
- Assemble chassis and thrusters as early as possible → hand off to GNC for code testing
- Place GNC sensors during assembly
- Once competition tasks release: begin printing claw parts (may overlap with finals — okay to push to spring)

### Spring Semester

- Assemble claw with ROV
- Test and verify; if no issues, hand off to GNC for code integration
