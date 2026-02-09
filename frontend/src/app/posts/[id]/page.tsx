'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { Calendar, Tag, Download, Trash2, Copy, Check } from 'lucide-react'
import toast from 'react-hot-toast'
import { postsAPI } from '@/lib/api'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'
import Header from '@/components/Header'
import LoadingSpinner from '@/components/LoadingSpinner'
import { useUser } from '@/contexts/UserContext'

interface Post {
  id: number
  slug: string
  title: string
  content: string | null
  thumbnail: string | null
  tags: string | null
  velog_published_at: string | null
  last_backed_up: string | null
}

export default function PostDetailPage() {
  const router = useRouter()
  const params = useParams()
  const { user, isLoading: userLoading } = useUser()
  const [post, setPost] = useState<Post | null>(null)
  const [postLoading, setPostLoading] = useState(true)
  const [copied, setCopied] = useState(false)

  const loadPost = useCallback(async (postId: number) => {
    try {
      const response = await postsAPI.getOne(postId)
      setPost(response.data)
    } catch (error) {
      toast.error('포스트를 불러오는데 실패했습니다')
      router.push('/posts')
    } finally {
      setPostLoading(false)
    }
  }, [router])

  useEffect(() => {
    if (!userLoading && !user) {
      router.push('/')
    }
  }, [user, userLoading, router])

  useEffect(() => {
    if (params.id && user) {
      loadPost(Number(params.id))
    }
  }, [params.id, user, loadPost])

  const handleDelete = async () => {
    if (!post) return
    if (!confirm(`"${post.title}" 포스트를 삭제하시겠습니까?`)) return

    try {
      await postsAPI.delete(post.id)
      toast.success('포스트가 삭제되었습니다')
      router.push('/posts')
    } catch (error) {
      toast.error('포스트 삭제에 실패했습니다')
    }
  }

  const handleDownload = () => {
    if (!post?.content) {
      toast.error('다운로드할 내용이 없습니다')
      return
    }

    const blob = new Blob([post.content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${post.slug}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleCopy = async () => {
    if (!post?.content) return

    try {
      await navigator.clipboard.writeText(post.content)
      setCopied(true)
      toast.success('클립보드에 복사되었습니다')
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      toast.error('복사에 실패했습니다')
    }
  }

  const parseTags = (tagsStr: string | null): string[] => {
    if (!tagsStr) return []
    try {
      return JSON.parse(tagsStr)
    } catch {
      return []
    }
  }

  if (userLoading) return <LoadingSpinner />

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header user={user} />

      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {postLoading ? (
          <div className="flex justify-center py-16">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : !post ? (
          <div className="flex justify-center py-16">
            <p className="text-gray-600 dark:text-gray-400">포스트를 찾을 수 없습니다</p>
          </div>
        ) : (<>
        {/* Post Header */}
        <div className="card mb-6">
          <h1 className="text-3xl font-bold mb-4">{post.title}</h1>

          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-4">
            {post.velog_published_at && (
              <span className="flex items-center gap-1">
                <Calendar size={14} />
                {format(new Date(post.velog_published_at), 'yyyy년 MM월 dd일', { locale: ko })}
              </span>
            )}
            {post.last_backed_up && (
              <span>
                마지막 백업: {format(new Date(post.last_backed_up), 'yyyy/MM/dd HH:mm')}
              </span>
            )}
          </div>

          {parseTags(post.tags).length > 0 && (
            <div className="flex items-center gap-2 mb-4">
              <Tag size={14} className="text-gray-400" />
              {parseTags(post.tags).map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs rounded"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          <div className="flex gap-2">
            <button onClick={handleCopy} className="btn btn-secondary flex items-center gap-1">
              {copied ? <Check size={16} /> : <Copy size={16} />}
              {copied ? '복사됨' : '복사'}
            </button>
            <button onClick={handleDownload} className="btn btn-secondary flex items-center gap-1">
              <Download size={16} />
              다운로드
            </button>
            <button onClick={handleDelete} className="btn btn-secondary text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/30 flex items-center gap-1">
              <Trash2 size={16} />
              삭제
            </button>
          </div>
        </div>

        {/* Post Content */}
        <div className="card">
          <h2 className="text-lg font-bold mb-4">마크다운 내용</h2>
          {post.content ? (
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto whitespace-pre-wrap text-sm font-mono">
              {post.content}
            </pre>
          ) : (
            <p className="text-gray-500 dark:text-gray-400">저장된 내용이 없습니다</p>
          )}
        </div>
        </>)}
      </main>
    </div>
  )
}
