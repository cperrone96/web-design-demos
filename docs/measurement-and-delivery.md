# Measurement and delivery handoff

This document records the implementation boundary for the fictional demonstrations
in this repository. It is an architecture and QA artifact, not evidence of live
traffic, conversions, SEO rankings, or client outcomes.

## Current implementation

```text
static HTML/CSS + local assets
        |
        v
static host/CDN (deployment-specific)
        |
        v
optional owner-controlled analytics configuration
        |
        v
GA4 events -> reporting/dashboard layer
```

The checked-in sites stop at the static HTML/CSS layer. No production GA4 property,
tracking ID, form destination, CRM connection, or customer dataset is included.
The contact, booking, and newsletter forms use native browser validation followed
by a local-only confirmation; their submit handlers prevent network transmission.
For a JavaScript-free browser, each form uses a POST to a hidden local `data:`
fallback target and displays a `<noscript>` notice. This avoids sending fields to
the current page or an external service.
This keeps the repository safe to share and makes the deployment boundary explicit.

## Privacy-safe event contract

If an owner later enables analytics, the implementation should use an approved
consent flow and send only event metadata. A suggested contract is:

| Event | When | Allowed parameters | Never send |
|---|---|---|---|
| `form_start` | Visitor focuses the first field | `site_demo`, `page_type`, `form_context` | Name, email, phone, address, free text |
| `generate_lead` | A form is successfully submitted | `site_demo`, `page_type`, `form_context` | Form payload, identifiers, health/financial details |
| `select_cta` | Visitor selects a primary CTA | `site_demo`, `page_type`, `cta_location`, `cta_type` | URL query values containing PII |

Parameter values should be controlled vocabularies rather than user-entered text.
Form handling, retention, consent, access controls, and dashboard ownership belong
to the site owner and deployment environment—not to this public source repository.

## Reporting dimensions

The static information architecture supports a consistent reporting taxonomy:

- `site_demo`: `green_horizons`, `climate_pro`, or `shield_pest`
- `page_type`: `home`, `service`, `service_area`, `faq`, `review`, `contact`,
  `booking`, `financing`, `emergency`, or `blog`
- `form_context`: the visible business purpose, such as `quote_request` or
  `service_booking`
- `cta_location`: `header`, `hero`, `content`, `footer`, or `mobile_menu`

These labels are a proposed measurement vocabulary. They do not imply that data is
currently collected or that a dashboard has live traffic to display.

## Delivery and QA gate

Before a real deployment, the owner should verify:

1. Every internal link and asset resolves from the deployed base path.
2. Keyboard navigation, visible focus, form labels, heading order, color contrast,
   and mobile layouts pass a browser accessibility review.
3. Forms use an approved processor and do not send sensitive data to analytics.
4. Consent behavior and privacy notice match the deployment jurisdiction.
5. Analytics events fire only after consent, use the approved parameter vocabulary,
   and exclude form contents and direct identifiers.
6. A test submission is removed from the production system after verification.
7. The deployed URL, release date, and owner are recorded outside this repository.

The repository's automated gate covers static checks only. It cannot prove remote
hosting availability, browser behavior, analytics configuration, or business
outcomes.
