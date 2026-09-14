# Web Design Demos

Static, hand-built marketing-site demonstrations for three fictional local-service
businesses. This repository is business/web-delivery evidence—not a data-science
portfolio project. It shows how I translate a business brief into information
architecture, responsive interface code, conversion paths, and a measurement-ready
handoff without exposing client systems or customer data.

## Portfolio boundary

- **All three businesses, metrics, testimonials, phone numbers, and email addresses
  are fictional demonstration content.** They are not client results or references.
- No customer records, production analytics exports, credentials, tracking IDs, or
  proprietary implementation details are stored here.
- The source contains no production analytics collection. The measurement contract
  and privacy-safe handoff are documented in
  [`docs/measurement-and-delivery.md`](docs/measurement-and-delivery.md).
- The repo is intentionally excluded from the data-science project pins. It supports
  applications that value web analytics, reporting, conversion measurement, and
  cross-functional delivery.

## Demonstrations

| Site | Business brief | Pages | Source preview |
|---|---|---:|---|
| **Green Horizons** | Landscaping and lawn care | 8 | [`green-horizons/index.html`](green-horizons/index.html) |
| **Climate Pro** | HVAC: heating, cooling, and emergency service | 16 | [`climate-pro/index.html`](climate-pro/index.html) |
| **Shield Pest** | Residential pest control | 4 | [`shield-pest/index.html`](shield-pest/index.html) |

The source previews work from a local static server or a static-host deployment.
The former `datadesigndynamics.org/demos/...` URLs are not presented as live
portfolio links because their current deployment status has not been verified.

## What the work demonstrates

### Product and delivery

- Brief-to-site translation for local-service audiences
- Page hierarchy and navigation across service, FAQ, service-area, review, contact,
  booking, financing, and emergency flows
- Conversion-oriented calls to action with clear next steps
- Reusable layout and component patterns implemented without a page builder

### Front-end implementation

- Semantic HTML with document language, titles, descriptions, landmarks, and
  descriptive image alternatives
- Responsive, mobile-first CSS with a separate visual system for each brand
- Lightweight static delivery: no framework runtime, build step, or hidden service
  dependency is required
- Local assets and relative links suitable for static hosting

### Measurement-ready handoff

- Form and CTA surfaces are identifiable without sending form contents to analytics
- Page taxonomy supports reporting by site, page type, and conversion surface
- The repository documents a privacy-safe event contract, ownership boundaries, and
  a pre-launch QA checklist rather than claiming unverified traffic or ROI

## Run locally

Python's standard-library server is sufficient; there is no package installation or
build step.

```bash
python3 -m http.server 8000
# open http://localhost:8000/green-horizons/
```

Run the deterministic quality gate from the repository root:

```bash
python3 scripts/validate_static_sites.py
```

The validator checks every HTML page for required metadata, image alternatives,
local asset/link integrity, and accidental credentials or machine-local paths. It
also reports page counts for the three demonstrations. Remote deployment checks
remain a release-owner responsibility because this repository does not control the
hosting account.

## License and reuse

The code is provided for portfolio review. Do not treat the fictional business
content, imagery, testimonials, or contact details as real-world claims. See
[`LICENSE`](LICENSE) for the code-usage terms.

---

Built for Data Design Dynamics as a demonstration portfolio. No client-confidential
information is included.
