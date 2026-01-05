# @dorc/clients - TypeScript SDK

TypeScript SDK for DORC API.

## Status

This is a **stub implementation** created to unblock `dorc.ai` development. Full implementation is pending.

## Installation

This package is installed via git URL in `dorc.ai`:

```json
{
  "dependencies": {
    "@dorc/clients": "git+https://github.com/dorc-io/dorc-clients.git#main"
  }
}
```

## Usage

```typescript
import { DorcClient } from '@dorc/clients'

const client = new DorcClient('https://dorc-api.example.com')
client.setToken('your-token')

// Methods will be implemented
```

## Development

```bash
npm install
npm run build
```

## TODO

- [ ] Implement validate() method
- [ ] Implement getRun() method
- [ ] Implement getChunks() method
- [ ] Implement thread methods
- [ ] Implement corpus methods
- [ ] Add proper error handling
- [ ] Add request/response types
- [ ] Add authentication helpers
