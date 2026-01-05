/**
 * @dorc/clients - TypeScript SDK
 * 
 * This is a stub implementation. Full SDK methods will be implemented later.
 */

export interface ValidateParams {
  tenantSlug: string
  candidate: {
    content: string
    sourceId?: string
    tags?: string[]
  }
  mode?: 'audit' | 'build-corpus' | 'use-corpus'
  options?: {
    useRag?: boolean
    focus?: string[]
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
}

export interface ValidationChunk {
  id: string
  status: 'pass' | 'warn' | 'fail'
  content: string
  findings: string[]
  suggestions?: string[]
}

export class DorcClient {
  private apiUrl: string
  private token: string | null = null

  constructor(apiUrl: string) {
    this.apiUrl = apiUrl
  }

  setToken(token: string | null): void {
    this.token = token
  }

  getToken(): string | null {
    return this.token
  }

  /**
   * Validate a candidate document
   * TODO: Implement actual API call
   */
  async validate(params: ValidateParams): Promise<ValidationRun> {
    throw new Error('SDK method not yet implemented - validate')
  }

  /**
   * Get validation run status
   * TODO: Implement actual API call
   */
  async getRun(runId: string): Promise<ValidationRun> {
    throw new Error('SDK method not yet implemented - getRun')
  }

  /**
   * Get chunks for a validation run
   * TODO: Implement actual API call
   */
  async getChunks(runId: string): Promise<ValidationChunk[]> {
    throw new Error('SDK method not yet implemented - getChunks')
  }

  /**
   * List threads
   * TODO: Implement actual API call
   */
  async listThreads(): Promise<any[]> {
    throw new Error('SDK method not yet implemented - listThreads')
  }

  /**
   * Get thread
   * TODO: Implement actual API call
   */
  async getThread(threadId: string): Promise<any> {
    throw new Error('SDK method not yet implemented - getThread')
  }

  /**
   * Create thread
   * TODO: Implement actual API call
   */
  async createThread(params: any): Promise<any> {
    throw new Error('SDK method not yet implemented - createThread')
  }

  /**
   * List corpora
   * TODO: Implement actual API call
   */
  async listCorpora(): Promise<any[]> {
    throw new Error('SDK method not yet implemented - listCorpora')
  }

  /**
   * Get corpus
   * TODO: Implement actual API call
   */
  async getCorpus(slug: string): Promise<any> {
    throw new Error('SDK method not yet implemented - getCorpus')
  }
}
