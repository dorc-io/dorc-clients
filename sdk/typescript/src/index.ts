/**
 * @dorc/clients - TypeScript SDK
 * 
 * TypeScript SDK for interacting with the DORC API.
 */

// Error types
export class DorcError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public code?: string
  ) {
    super(message)
    this.name = 'DorcError'
  }
}

// Type definitions
export interface ValidateParams {
  tenantSlug: string
  candidate: {
    content: string
    cce_id?: string
    title?: string
    source?: string
    labels?: Record<string, string>
  }
  mode?: 'audit' | 'rectify' | 'smoke'
  options?: {
    chunking?: {
      max_chars?: number
      overlap_chars?: number
    }
    models?: {
      primary?: string
      fallback?: string
    }
  }
}

export interface ValidationRun {
  id: string
  status: 'queued' | 'running' | 'succeeded' | 'failed'
  summary?: {
    pass: number
    warn: number
    fail: number
  }
  message?: string
}

export interface ValidationChunk {
  id: string
  status: 'pass' | 'warn' | 'fail'
  content: string
  findings: string[]
  suggestions?: string[]
}

export interface Corpus {
  id: string
  slug: string
  name: string
  createdAt: Date
}

export interface Thread {
  id: string
  name: string
  createdAt: Date
  updatedAt: Date
  messageCount: number
  tenantSlug?: string
}

export interface ThreadMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
}

export interface ChatParams {
  provider: 'openai' | 'gemini' | 'custom'
  preference: 'dorc-shared-gemini' | 'dorc-shared-openai' | 'my-keys-gemini' | 'my-keys-openai' | 'byo-ai'
  messages: Array<{
    role: 'user' | 'assistant' | 'system'
    content: string
  }>
  api_key?: string
  custom_endpoint?: string
  custom_token?: string
  model?: string
  temperature?: number
  thread_id?: string
}

export interface ChatResponse {
  content: string
  model?: string
  usage?: {
    prompt_tokens?: number
    completion_tokens?: number
    total_tokens?: number
  }
  thread_id?: string
}

export class DorcClient {
  private apiUrl: string
  private token: string | null = null

  constructor(apiUrl: string) {
    this.apiUrl = apiUrl.replace(/\/$/, '') // Remove trailing slash
  }

  setToken(token: string | null): void {
    this.token = token
  }

  getToken(): string | null {
    return this.token
  }

  /**
   * Internal HTTP request helper
   */
  private async _request<T>(
    method: string,
    path: string,
    body?: any,
    queryParams?: Record<string, string>
  ): Promise<T> {
    // #region agent log
    fetch(`${this.apiUrl}/v1/debug/log`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sdk/index.ts:135',message:'_request: called',data:{method,path,hasToken:!!this.token,tokenLength:this.token?.length||0},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
    // #endregion
    if (!this.token) {
      // #region agent log
      fetch(`${this.apiUrl}/v1/debug/log`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sdk/index.ts:137',message:'_request: no token error',data:{method,path},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
      // #endregion
      throw new DorcError('Authentication token is required. Call setToken() first.', 401, 'AUTH_REQUIRED')
    }

    const url = new URL(path, this.apiUrl)
    if (queryParams) {
      Object.entries(queryParams).forEach(([key, value]) => {
        url.searchParams.append(key, value)
      })
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.token}`,
    }

    const options: RequestInit = {
      method,
      headers,
    }

    if (body && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      options.body = JSON.stringify(body)
    }

    try {
      // #region agent log
      fetch(`${this.apiUrl}/v1/debug/log`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sdk/index.ts:161',message:'_request: making fetch',data:{method,url:url.toString(),hasToken:!!this.token,tokenLength:this.token?.length||0},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
      // #endregion
      const response = await fetch(url.toString(), options)
      // #region agent log
      fetch(`${this.apiUrl}/v1/debug/log`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sdk/index.ts:163',message:'_request: got response',data:{method,path,status:response.status,statusText:response.statusText,ok:response.ok},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
      // #endregion

      // Handle error responses
      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`
        let errorCode: string | undefined
        let errorDetail: string | undefined

        try {
          const errorBody = await response.json()
          if (errorBody.error?.message) {
            errorMessage = errorBody.error.message
          }
          if (errorBody.error?.code) {
            errorCode = errorBody.error.code
          }
          if (errorBody.detail) {
            errorDetail = errorBody.detail
          }
        } catch {
          // If JSON parsing fails, try to get text
          try {
            const errorText = await response.text()
            errorDetail = errorText.substring(0, 200)
          } catch {
            // If text parsing also fails, use default error message
          }
        }

        // Map status codes to error types
        if (response.status === 401) {
          throw new DorcError('Authentication failed. Please check your token.', 401, errorCode || 'AUTH_FAILED')
        } else if (response.status === 403) {
          throw new DorcError('Permission denied. You do not have access to this resource.', 403, errorCode || 'PERMISSION_DENIED')
        } else if (response.status === 404) {
          throw new DorcError('Resource not found.', 404, errorCode || 'NOT_FOUND')
        } else if (response.status === 400) {
          throw new DorcError(errorMessage, 400, errorCode || 'BAD_REQUEST')
        } else if (response.status >= 500) {
          throw new DorcError('Server error. Please try again later.', response.status, errorCode || 'SERVER_ERROR')
        } else {
          throw new DorcError(errorMessage, response.status, errorCode)
        }
      }

      // Parse successful response
      const data = await response.json()
      return data as T
    } catch (error) {
      if (error instanceof DorcError) {
        throw error
      }
      // Network or other errors
      throw new DorcError(
        `Request failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        undefined,
        'NETWORK_ERROR'
      )
    }
  }

  /**
   * Validate a candidate document
   */
  async validate(params: ValidateParams): Promise<ValidationRun> {
    const requestBody = {
      mode: params.mode || 'audit',
      candidate: {
        content: params.candidate.content,
        content_type: 'text/markdown' as const,
        cce_id: params.candidate.cce_id,
        title: params.candidate.title,
        source: params.candidate.source,
        labels: params.candidate.labels,
      },
      options: params.options || {},
    }

    const response = await this._request<{
      run_id: string
      links?: {
        run?: string
        chunks?: string
      }
    }>('POST', '/v1/validate', requestBody)

    return {
      id: response.run_id,
      status: 'queued',
    }
  }

  /**
   * Get validation run status
   */
  async getRun(runId: string): Promise<ValidationRun> {
    const response = await this._request<{
      run_id: string
      status?: string
      pipeline_status?: string
      summary?: {
        pass: number
        warn: number
        fail: number
      }
      message?: string
    }>('GET', `/v1/runs/${runId}`)

    // Map API status to SDK status
    // Engine returns pipeline_status: "COMPLETE", "RUNNING", etc.
    // Also check for status field as fallback
    const statusValue = response.pipeline_status || response.status || 'QUEUED'
    let status: 'queued' | 'running' | 'succeeded' | 'failed' = 'queued'
    
    if (statusValue === 'COMPLETE' || statusValue === 'COMPLETED' || statusValue === 'SUCCEEDED' || statusValue === 'succeeded') {
      status = 'succeeded'
    } else if (statusValue === 'FAILED' || statusValue === 'ERROR' || statusValue === 'failed') {
      status = 'failed'
    } else if (statusValue === 'RUNNING' || statusValue === 'PROCESSING' || statusValue === 'running') {
      status = 'running'
    }

    return {
      id: response.run_id,
      status,
      summary: response.summary,
      message: response.message,
    }
  }

  /**
   * Get chunks for a validation run
   */
  async getChunks(runId: string): Promise<ValidationChunk[]> {
    const response = await this._request<{
      chunks: Array<{
        chunk_id?: string
        id?: string
        status: string
        content: string
        findings?: string[]
        message?: string
        finding_count?: number
        evidence?: Array<{
          type?: string
          summary?: string
          candidate_quote?: string
          canon_quote?: string
          canon_quotes?: string[]
          sources?: string[]
        }>
        suggestions?: string[]
      }>
    }>('GET', `/v1/runs/${runId}/chunks`)

    return (response.chunks || []).map((chunk) => {
      // Map API status to SDK status
      let status: 'pass' | 'warn' | 'fail' = 'pass'
      if (chunk.status === 'WARN' || chunk.status === 'warning') {
        status = 'warn'
      } else if (chunk.status === 'FAIL' || chunk.status === 'failed' || chunk.status === 'error') {
        status = 'fail'
      }

      // Extract findings from multiple sources:
      // 1. Direct findings array (if present)
      // 2. Message field (engine's primary finding message)
      // 3. Evidence items (if they contain finding summaries)
      const findings: string[] = []
      
      // Add direct findings array if present
      if (chunk.findings && Array.isArray(chunk.findings)) {
        findings.push(...chunk.findings.filter(f => f && f.trim().length > 0))
      }
      
      // Add message as a finding if it exists and isn't already in findings
      if (chunk.message && chunk.message.trim()) {
        const message = chunk.message.trim()
        // Only add if it's not a generic message and not already in findings
        if (message && !findings.includes(message) && message !== 'pass' && message !== 'smoke') {
          findings.push(message)
        }
      }
      
      // Extract findings from evidence items
      if (chunk.evidence && Array.isArray(chunk.evidence)) {
        for (const evidence of chunk.evidence) {
          if (evidence.summary && evidence.summary.trim() && !findings.includes(evidence.summary.trim())) {
            findings.push(evidence.summary.trim())
          }
          // Also check for contradiction details in evidence
          if (evidence.type === 'contradiction' && evidence.candidate_quote && evidence.canon_quote) {
            const contradictionMsg = `Contradiction found: "${evidence.candidate_quote}" conflicts with corpus: "${evidence.canon_quote}"`
            if (!findings.includes(contradictionMsg)) {
              findings.push(contradictionMsg)
            }
          }
        }
      }

      return {
        id: chunk.chunk_id || chunk.id || '',
        status,
        content: chunk.content || '',
        findings: findings.length > 0 ? findings : [],
        suggestions: chunk.suggestions,
      }
    })
  }

  /**
   * List all corpora (tenants) the user has access to
   */
  async listCorpora(): Promise<Corpus[]> {
    const response = await this._request<{
      tenants: Array<{
        tenant_slug: string
        created_at?: number
        name?: string
      }>
    }>('GET', '/v1/corpora')

    return (response.tenants || []).map((tenant) => ({
      id: tenant.tenant_slug,
      slug: tenant.tenant_slug,
      name: tenant.name || tenant.tenant_slug,
      createdAt: tenant.created_at ? new Date(tenant.created_at * 1000) : new Date(),
    }))
  }

  /**
   * Get a specific corpus by slug
   */
  async getCorpus(slug: string): Promise<Corpus | null> {
    const corpora = await this.listCorpora()
    return corpora.find((c) => c.slug === slug) || null
  }

  /**
   * Create a new corpus (tenant)
   */
  async createCorpus(params: { slug: string; name?: string }): Promise<Corpus> {
    const response = await this._request<{
      tenant_slug: string
      created_at: number
    }>('POST', '/v1/corpora', {
      tenant_slug: params.slug,
    })

    return {
      id: response.tenant_slug,
      slug: response.tenant_slug,
      name: params.name || response.tenant_slug,
      createdAt: new Date(response.created_at * 1000),
    }
  }

  /**
   * Update a corpus (tenant) name
   */
  async updateCorpus(slug: string, params: { name: string }): Promise<Corpus> {
    await this._request('PUT', `/v1/corpora/${slug}`, {
      name: params.name,
    })

    // Return updated corpus by fetching it
    const corpus = await this.getCorpus(slug)
    if (!corpus) {
      throw new DorcError('Corpus not found after update', 404, 'NOT_FOUND')
    }
    return corpus
  }

  /**
   * Delete a corpus (tenant)
   */
  async deleteCorpus(slug: string): Promise<void> {
    await this._request('DELETE', `/v1/corpora/${slug}`)
  }

  /**
   * List all chat threads for a tenant
   */
  async listThreads(tenantSlug: string): Promise<Thread[]> {
    const response = await this._request<{
      threads: Array<{
        thread_id: string
        name: string
        created_at: number
        updated_at: number
        message_count: number
      }>
    }>('GET', '/v1/ai/threads', undefined, {
      tenant_slug: tenantSlug,
    })

    return (response.threads || []).map((thread) => ({
      id: thread.thread_id,
      name: thread.name,
      createdAt: new Date(thread.created_at * 1000),
      updatedAt: new Date(thread.updated_at * 1000),
      messageCount: thread.message_count,
      tenantSlug,
    }))
  }

  /**
   * Get a specific thread by ID
   * Note: This filters from listThreads since there's no direct GET endpoint
   */
  async getThread(threadId: string, tenantSlug: string): Promise<Thread | null> {
    const threads = await this.listThreads(tenantSlug)
    return threads.find((t) => t.id === threadId) || null
  }

  /**
   * Create a new chat thread
   */
  async createThread(params: { tenantSlug: string; name: string }): Promise<Thread> {
    const response = await this._request<{
      thread_id: string
      name: string
      created_at: number
      updated_at: number
      message_count: number
    }>('POST', '/v1/ai/threads', {
      tenant_slug: params.tenantSlug,
      name: params.name,
    })

    return {
      id: response.thread_id,
      name: response.name,
      createdAt: new Date(response.created_at * 1000),
      updatedAt: new Date(response.updated_at * 1000),
      messageCount: response.message_count,
      tenantSlug: params.tenantSlug,
    }
  }

  /**
   * Update a chat thread's name
   */
  async updateThread(threadId: string, params: { name: string }): Promise<Thread> {
    const response = await this._request<{
      thread_id: string
      name: string
      created_at: number
      updated_at: number
      message_count: number
    }>('PUT', `/v1/ai/threads/${threadId}`, {
      name: params.name,
    })

    return {
      id: response.thread_id,
      name: response.name,
      createdAt: new Date(response.created_at * 1000),
      updatedAt: new Date(response.updated_at * 1000),
      messageCount: response.message_count,
    }
  }

  /**
   * Delete a chat thread
   */
  async deleteThread(threadId: string): Promise<void> {
    await this._request('DELETE', `/v1/ai/threads/${threadId}`)
  }

  /**
   * Get messages from a chat thread
   */
  async getThreadMessages(threadId: string): Promise<ThreadMessage[]> {
    const response = await this._request<{
      messages: Array<{
        role: 'user' | 'assistant' | 'system'
        content: string
        timestamp: number
      }>
    }>('GET', `/v1/ai/threads/${threadId}/messages`)

    return (response.messages || []).map((msg, index) => ({
      id: `${threadId}-${index}`,
      role: msg.role,
      content: msg.content,
      timestamp: new Date(msg.timestamp * 1000),
    }))
  }

  /**
   * Send a chat message and get AI response
   */
  async chat(params: ChatParams): Promise<ChatResponse> {
    const requestBody: any = {
      provider: params.provider,
      preference: params.preference,
      messages: params.messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      })),
    }

    if (params.api_key) {
      requestBody.api_key = params.api_key
    }
    if (params.custom_endpoint) {
      requestBody.custom_endpoint = params.custom_endpoint
    }
    if (params.custom_token) {
      requestBody.custom_token = params.custom_token
    }
    if (params.model) {
      requestBody.model = params.model
    }
    if (params.temperature !== undefined) {
      requestBody.temperature = params.temperature
    }
    if (params.thread_id) {
      requestBody.thread_id = params.thread_id
    }

    const response = await this._request<{
      content: string
      model?: string
      usage?: {
        prompt_tokens?: number
        completion_tokens?: number
        total_tokens?: number
      }
      thread_id?: string
    }>('POST', '/v1/ai/chat', requestBody)

    return {
      content: response.content,
      model: response.model,
      usage: response.usage,
      thread_id: response.thread_id,
    }
  }

  /**
   * Create a document in the library
   */
  async createDocument(params: {
    tenantSlug: string
    title: string
    content: string
    docSlug?: string
    folderPath?: string
    validation?: {
      runId: string
      result: 'PASS' | 'WARN' | 'FAIL' | 'ERROR'
    }
  }): Promise<{ doc_slug: string; version: string }> {
    const requestBody: any = {
      title: params.title,
      content: params.content,
      content_type: 'text/markdown',
    }

    if (params.docSlug) {
      requestBody.doc_slug = params.docSlug
    }

    if (params.folderPath) {
      requestBody.folder_path = params.folderPath
    }

    if (params.validation) {
      requestBody.validation = {
        run_id: params.validation.runId,
        result: params.validation.result,
      }
    }

    const response = await this._request<{
      tenant_slug: string
      doc_slug: string
      version: string
    }>('POST', '/v1/library/docs', requestBody)

    return {
      doc_slug: response.doc_slug,
      version: response.version,
    }
  }
}
