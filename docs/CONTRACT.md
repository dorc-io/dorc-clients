# DORC AUTHENTICATION & ACCESS CONTRACT (LOCKED)

## Status
This section is NORMATIVE. Implementations MUST comply.

---

## 1. Authentication Model (Authoritative)

### 1.1 Capability-Based Authentication (REQUIRED)

All external access to DORC systems (MCP, Engine) MUST use
**capability-based authentication**, not identity-based authentication.

The system does NOT perform:
- user login
- OAuth authorization flows
- OIDC redirects
- token exchange
- token refresh

These mechanisms are explicitly OUT OF SCOPE.

---

## 2. Token Type (REQUIRED)

### 2.1 Bearer Tokens

All authenticated requests MUST include:

Authorization: Bearer <token>

The token MAY be:
- a static API key, OR
- a self-issued JWT signed by DORC

Both are treated identically as **capability tokens**.

---

## 3. JWT Requirements (When JWTs Are Used)

When JWTs are used, they MUST:

- be signed by DORC (HS256)
- be verifiable offline (no IdP calls)
- include the following claims:

Required claims:
- iss: "dorc"
- sub: capability identifier (NOT a human user)
- tenant: tenant_slug
- scope: list of allowed operations
- iat: issued-at timestamp
- exp: expiration timestamp

JWTs are NOT identity tokens.
JWTs are capability tokens with structure.

---

## 4. Platform Compatibility (MANDATORY)

The authentication mechanism MUST be compatible with:
- ChatGPT agents
- Gemini Gems
- MCP tool calls

This implies:
- no OAuth
- no OIDC
- no Google I A M
- no interactive authentication

Tokens MUST be static strings that can be injected into HTTP headers.

---

## 5. MCP Responsibilities

The MCP MUST:
- accept Bearer tokens
- validate token signature (if JWT)
- extract tenant and scope from token
- enforce scope-based authorization
- forward requests to the Engine using the SAME token

The MCP is the ONLY externally exposed programmable interface.

---

## 6. Engine Responsibilities

The Engine MUST:
- accept Bearer tokens ONLY from MCP
- validate token signature
- trust tenant and scope as conveyed by the token
- reject unauthenticated requests

The Engine MUST NOT expose public endpoints.

---

## 7. SDK Responsibilities

The Client SDK MUST:
- accept a token string from the caller
- attach it as Authorization: Bearer <token>
- NOT generate tokens
- NOT manage authentication flows

The SDK is a transport convenience only.

---

## 8. Health Endpoints

The following endpoints MUST exist:
- /healthz (platform / infra health)
- /health  (application health)

Health endpoints MUST NOT require authentication.

---

## 9. Explicit Non-Goals

The system explicitly does NOT support:
- OAuth 2.0
- OpenID Connect
- Google I A M
- user login sessions
- refresh tokens

Any implementation attempting to add these is NON-COMPLIANT.

---

## 10. Summary (Intent Lock)

DORC authentication is:
- simple
- explicit
- capability-based
- agent-compatible

Bearer tokens are the interface contract.
JWTs are an internal format choice, not a protocol choice.
