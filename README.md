# AI Alcohol App

Current status: working frontend/backend scaffold with placeholder verification only.

## Local Run

Backend:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 3001
```

Frontend:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open `http://127.0.0.1:5173`.

## Current Features

- Upload one label image
- Manually enter expected fields
- Submit to backend `/verify`
- Display placeholder `Match` / `Mismatch` / `Needs Review` results
- Backend health check at `GET /health`

## Current Limitations

- No OCR yet
- No AI extraction yet
- No persistence
- Placeholder verification logic only
- Frontend is JavaScript; backend is FastAPI/Python

# **Take-Home Project: AI-Powered Alcohol Label Verification App**

## **Project Background & Stakeholder Context**

*The following document contains notes from our discovery sessions with the Compliance Division, along with technical requirements for the prototype. We've included stakeholder feedback to give you context on how this tool will be used.*

### **Interview Notes: Sarah Chen, Deputy Director of Label Compliance**

"TTB reviews about 150,000 label applications a year. Our team of 47 agents handles all of them.

The actual review process:
 An agent pulls up an application, looks at the label artwork, and checks that what's on the label matches what's in the application. Brand name matches? Check. ABV is correct? Check. Government warning is there? Check. It takes maybe 5-10 minutes per application for a simple one, longer if there are issues.

This is what got leadership interested in AI—a lot of what we do is just matching. Just making sure the number on the form is the same as the number on the label. My agents spend half their day doing what's essentially data entry verification.

We tried a pilot with the scanning vendor last year. Disaster. The system would take 30, 40 seconds sometimes to process a single label. Our agents just went back to doing it by eye because they could do five labels in the time it took the machine to do one. **If we can't get results back in about 5 seconds, nobody's going to use it.**

The agents really vary in their tech comfort level. Dave's been here since for 25 years and still prints his emails. Meanwhile, Jenny's fresh out of college and probably could have built this tool herself. We need something an old lady can use. Half our team is over 50. Clean, obvious, no hunting for buttons.

We get these big importers who dump 200, 300 label applications on us at once. Right now we literally have to process them one at a time. If there was some way to **handle batch uploads**, that would be huge."

### **Interview Notes: Marcus Williams, IT Systems Administrator**

"Technical landscape:

Our current infrastructure is government infrastructure. We're on Azure now after the migration in 2019.

The COLA system is built on .NET.

For this prototype, we're not looking to integrate with COLA directly. Think of this as a standalone proof-of-concept that could potentially inform future procurement decisions.

Security-wise, just don't do anything crazy.

Our network blocks outbound traffic to a lot of domains, so keep that in mind if you're thinking about cloud APIs. Our firewall blocks connections to ML endpoints."

### **Interview Notes: Dave Morrison, Senior Compliance Agent (28 years)**

"You can't just pattern match everything. I had one last week where the brand name was 'STONE'S THROW' on the label but 'Stone's Throw' in the application. Technically a mismatch? Sure. But it's obviously the same thing."

### **Interview Notes: Jenny Park, Junior Compliance Agent (8 months)**

"I literally have a printed checklist on my desk that I go through for every label. Brand name—check. ABV—check. Warning statement—check.

The warning statement has to be **exact**. The 'GOVERNMENT WARNING:' part has to be in all caps and bold. I caught one last month where they used 'Government Warning' in title case instead of all caps. Rejected.

The tool should handle images that aren't perfectly shot. I've seen labels that are photographed at weird angles, or the lighting is bad, or there's glare on the bottle. Right now if an agent can't read the label they just reject it and ask for a better image."

## **Technical Requirements**

You are free to use any programming languages, frameworks, or libraries you prefer. We want to see what kind of engineering, design, and integration decisions you make.

## **Additional Context**

### **About TTB Label Requirements**

For reference, TTB requires specific information on alcohol beverage labels. The exact requirements vary by beverage type (beer, wine, distilled spirits) but common elements include:

- Brand name
- Class/type designation
- Alcohol content (with some exceptions for certain wine/beer)
- Net contents
- Name and address of bottler/producer
- Country of origin for imports
- **Government Health Warning Statement** (mandatory on all alcohol beverages)

We encourage you to review TTB's guidelines at ttb.gov for additional context on label requirements.

### **Sample Label**

Your app should handle labels containing information like the example below:

**Example Distilled Spirits Label Fields:**

- Brand Name: "OLD TOM DISTILLERY"
- Class/Type: "Kentucky Straight Bourbon Whiskey"
- Alcohol Content: "45% Alc./Vol. (90 Proof)"
- Net Contents: "750 mL"
- Government Warning: \[Standard government warning text\]

*We encourage you to create or source additional test labels—AI image generation tools work well for this.*

## **Deliverables**

1. **Source Code Repository** (GitHub or similar)
   - All source code
   - README with setup and run instructions
   - Brief documentation of approach, tools used, assumptions made
2. **Deployed Application URL**
   - Working prototype we can access and test

## **Evaluation Criteria**

- Correctness and completeness of core requirements
- Code quality and organization
- Appropriate technical choices for the scope
- User experience and error handling
- Attention to requirements
- Creative problem-solving

A working core application with clean code is preferred over ambitious but incomplete features. Document any trade-offs or limitations.

*Questions? Reach out for clarification—though we also value how you fill in gaps independently.*
```
