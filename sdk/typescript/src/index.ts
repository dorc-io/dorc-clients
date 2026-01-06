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
    fetch('http://127.0.0.1:7242/ingest/d115584a-c16f-4404-8336-0f1c1969e079',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sdk/_request',message:'_request called',data:{method,path,hasToken:!!this.token,tokenLength:this.token?.length,tokenPreview:this.token?.substring(0,50)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    if (!this.token) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/d115584a-c16f-4404-8336-0f1c1969e079',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sdk/_request',message:'No token set',data:{method,path},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      throw new DorcError('Authentication token is required. Call setToken() first.', 401, 'AUTH_REQUIRED')
    }

    // Decode token to check algorithm
    let tokenAlg = 'unknown'
    try {
      const parts = this.token.split('.')
      if (parts.length === 3) {
        const header = JSON.parse(atob(parts[0]))
        tokenAlg = header.alg || 'unknown'
      }
    } catch (e) {
      // Ignore decode errors
    }

    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/d115584a-c16f-4404-8336-0f1c1969e079',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sdk/_request',message:'Token decoded',data:{method,path,tokenAlg,tokenLength:this.token.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion

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
      fetch('http://127.0.0.1:7242/ingest/d115584a-c16f-4404-8336-0f1c1969e079',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sdk/_request',message:'Making API request',data:{method,url:url.toString(),tokenAlg},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion

      const response = await fetch(url.toString(), options)

      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/d115584a-c16f-4404-8336-0f1c1969e079',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'sdk/_request',message:'API response received',data:{method,path,status:response.status,statusText:response.statusText,tokenAlg},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion

      // Handle error responses
      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`
        let errorCode: string | undefined

        try {
          const errorBody = await response.json()
          if (errorBody.error?.message) {
            errorMessage = errorBody.error.message
          }
          if (errorBody.error?.code) {
            errorCode = errorBody.error.code
          }
        } catch {
          // If JSON parsing fails, use default error message
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
      status: string
      summary?: {
        pass: number
        warn: number
        fail: number
      }
      message?: string
    }>('GET', `/v1/runs/${runId}`)

    // Map API status to SDK status
    let status: 'queued' | 'running' | 'succeeded' | 'failed' = 'queued'
    if (response.status === 'COMPLETED' || response.status === 'SUCCEEDED') {
      status = 'succeeded'
    } else if (response.status === 'FAILED' || response.status === 'ERROR') {
      status = 'failed'
    } else if (response.status === 'RUNNING' || response.status === 'PROCESSING') {
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
        findings: string[]
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

      return {
        id: chunk.chunk_id || chunk.id || '',
        status,
        content: chunk.content,
        findings: chunk.findings || [],
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
}
