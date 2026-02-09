'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { FileText, Calendar, Tag, Trash2, Download } from 'lucide-react'
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

export default function PostsPage() {
  const router = useRouter()
  const { user, isLoading: userLoading } = useUser()
  const [posts, setPosts] = useState<Post[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [postsLoading, setPostsLoading] = useState(true)
  const limit = 20

  useEffect(() => {
    if (!userLoading && !user) {
      router.push('/')
    }
  }, [user, userLoading])

  useEffect(() => {
    if (user) loadPosts()
  }, [page, user])

  const loadPosts = async () => {
    try {
      const response = await postsAPI.getAll(page, limit)
      setPosts(response.data.posts)
      setTotal(response.data.total)
    } catch (error) {
      toast.error('포스트를 불러오는데 실패했습니다')
      router.push('/dashboard')
    } finally {
      setPostsLoading(false)
    }
  }

  const handleDelete = async (postId: number, title: string) => {
    if (!confirm(`"${title}" 포스트를 삭제하시겠습니까?`)) return

    try {
      await postsAPI.delete(postId)
      toast.success('포스트가 삭제되었습니다')
      loadPosts()
    } catch (error) {
      toast.error('포스트 삭제에 실패했습니다')
    }
  }

  const handleDownload = (post: Post) => {
    if (!post.content) {
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

  const parseTags = (tagsStr: string | null): string[] => {
    if (!tagsStr) return []
    try {
      return JSON.parse(tagsStr)
    } catch {
      return []
    }
  }

  const totalPages = Math.ceil(total / limit)

  if (userLoading || postsLoading) return <LoadingSpinner />

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />

      <main className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">백업된 포스트</h1>
          <p className="text-gray-600">총 {total}개의 포스트가 서버에 저장되어 있습니다</p>
        </div>

        {posts.length === 0 ? (
          <div className="card text-center py-12">
            <FileText className="mx-auto text-gray-400 mb-4" size={48} />
            <p className="text-gray-600">백업된 포스트가 없습니다</p>
            <Link href="/dashboard" className="btn btn-primary mt-4 inline-block">
              백업 시작하기
            </Link>
          </div>
        ) : (
          <>
            <div className="space-y-4">
              {posts.map((post) => (
                <div key={post.id} className="card">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <Link
                        href={`/posts/${post.id}`}
                        className="text-xl font-bold hover:text-primary-600 transition-colors"
                      >
                        {post.title}
                      </Link>

                      <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                        {post.velog_published_at && (
                          <span className="flex items-center gap-1">
                            <Calendar size={14} />
                            {format(new Date(post.velog_published_at), 'yyyy년 MM월 dd일', { locale: ko })}
                          </span>
                        )}
                        {post.last_backed_up && (
                          <span>
                            백업: {format(new Date(post.last_backed_up), 'MM/dd HH:mm')}
                          </span>
                        )}
                      </div>

                      {parseTags(post.tags).length > 0 && (
                        <div className="flex items-center gap-2 mt-3">
                          <Tag size={14} className="text-gray-400" />
                          {parseTags(post.tags).map((tag, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleDownload(post)}
                        className="p-2 text-gray-500 hover:text-primary-600 transition-colors"
                        title="마크다운 다운로드"
                      >
                        <Download size={18} />
                      </button>
                      <button
                        onClick={() => handleDelete(post.id, post.title)}
                        className="p-2 text-gray-500 hover:text-red-600 transition-colors"
                        title="삭제"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-2 mt-8">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="btn btn-secondary"
                >
                  이전
                </button>
                <span className="px-4 py-2 text-gray-600">
                  {page} / {totalPages}
                </span>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="btn btn-secondary"
                >
                  다음
                </button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
