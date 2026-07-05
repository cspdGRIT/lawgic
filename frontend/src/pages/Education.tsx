import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { educationAPI } from '../lib/api'

const LEVEL_COLORS: Record<string, string> = {
  Beginner: 'bg-green-950 text-green-400',
  Intermediate: 'bg-yellow-950 text-yellow-400',
  Advanced: 'bg-red-950 text-red-400',
}

export default function Education() {
  const [selectedCourse, setSelectedCourse] = useState<any>(null)
  const [activeLesson, setActiveLesson] = useState<any>(null)
  const [quizMode, setQuizMode] = useState(false)
  const [answers, setAnswers] = useState<number[]>([])
  const [quizResult, setQuizResult] = useState<any>(null)

  const { data: courses = [] } = useQuery({
    queryKey: ['courses'],
    queryFn: () => educationAPI.getCourses(),
    select: (d: any) => d || [],
  })

  const { data: courseDetail } = useQuery({
    queryKey: ['course', selectedCourse?.id],
    queryFn: () => educationAPI.getCourse(selectedCourse.id),
    enabled: !!selectedCourse?.id,
    select: (d: any) => d,
  })

  const submitMutation = useMutation({
    mutationFn: (ans: number[]) => educationAPI.submitQuiz(selectedCourse.id, ans),
    onSuccess: (data: any) => setQuizResult(data),
  })

  function handleSelectCourse(course: any) {
    setSelectedCourse(course)
    setActiveLesson(null)
    setQuizMode(false)
    setAnswers([])
    setQuizResult(null)
  }

  function handleBack() {
    if (quizMode || activeLesson) {
      setQuizMode(false)
      setActiveLesson(null)
    } else {
      setSelectedCourse(null)
    }
  }

  // Quiz view
  if (quizMode && courseDetail) {
    const quiz = courseDetail.quiz || []

    if (quizResult) {
      return (
        <div className="max-w-2xl mx-auto">
          <button onClick={() => { setQuizMode(false); setQuizResult(null); setAnswers([]) }} className="text-gray-500 hover:text-white text-sm mb-6 transition-colors">← Back to course</button>
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 text-center">
            <div className="text-6xl mb-4">{quizResult.passed ? '🎉' : '📚'}</div>
            <h2 className="font-serif text-3xl font-bold text-white mb-2">{quizResult.score}%</h2>
            <p className="text-gray-400 mb-1">{quizResult.correct} of {quizResult.total} correct</p>
            <p className={`text-sm font-medium mb-8 ${quizResult.passed ? 'text-green-400' : 'text-yellow-400'}`}>
              {quizResult.message}
            </p>
            <div className="space-y-3 text-left mb-8">
              {quizResult.results?.map((r: any, i: number) => (
                <div key={i} className={`rounded-xl p-4 ${r.is_correct ? 'bg-green-950 border border-green-900' : 'bg-red-950 border border-red-900'}`}>
                  <p className="text-white text-sm font-medium mb-2">{r.question}</p>
                  <p className="text-xs text-gray-400">
                    Your answer: <span className={r.is_correct ? 'text-green-400' : 'text-red-400'}>{quiz[i]?.options[r.your_answer] || 'Not answered'}</span>
                    {!r.is_correct && <span className="ml-3 text-green-400">Correct: {quiz[i]?.options[r.correct_answer]}</span>}
                  </p>
                </div>
              ))}
            </div>
            <button onClick={() => { setAnswers([]); setQuizResult(null) }} className="bg-white text-black font-semibold px-8 py-3 rounded-xl text-sm hover:bg-gray-100 transition-colors">
              Retry Quiz
            </button>
          </div>
        </div>
      )
    }

    return (
      <div className="max-w-2xl mx-auto">
        <button onClick={() => setQuizMode(false)} className="text-gray-500 hover:text-white text-sm mb-6 transition-colors">← Back to course</button>
        <div className="mb-6">
          <h1 className="font-serif text-2xl font-bold text-white">Knowledge Check</h1>
          <p className="text-gray-500 text-sm mt-0.5">{courseDetail.title}</p>
        </div>
        <div className="space-y-6">
          {quiz.map((q: any, i: number) => (
            <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
              <p className="text-white font-medium mb-4 text-sm">
                <span className="text-gray-500 mr-2">Q{i + 1}.</span>
                {q.question}
              </p>
              <div className="space-y-2">
                {q.options.map((opt: string, j: number) => (
                  <button
                    key={j}
                    onClick={() => {
                      const newAnswers = [...answers]
                      newAnswers[i] = j
                      setAnswers(newAnswers)
                    }}
                    className={`w-full text-left px-4 py-3 rounded-lg text-sm transition-colors ${
                      answers[i] === j
                        ? 'bg-white text-black'
                        : 'bg-zinc-800 text-gray-400 hover:bg-zinc-700 hover:text-white'
                    }`}
                  >
                    <span className="mr-3 font-medium">{['A', 'B', 'C', 'D'][j]}.</span>{opt}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-6">
          <button
            onClick={() => submitMutation.mutate(answers)}
            disabled={answers.length < quiz.length || submitMutation.isPending}
            className="w-full bg-white text-black font-semibold py-3 rounded-xl text-sm hover:bg-gray-100 transition-colors disabled:opacity-50"
          >
            {submitMutation.isPending ? 'Submitting...' : `Submit Answers (${answers.filter((a) => a !== undefined).length}/${quiz.length} answered)`}
          </button>
        </div>
      </div>
    )
  }

  // Lesson view
  if (activeLesson) {
    return (
      <div className="max-w-3xl mx-auto">
        <button onClick={() => setActiveLesson(null)} className="text-gray-500 hover:text-white text-sm mb-6 transition-colors">
          ← Back to {selectedCourse?.title}
        </button>
        <div className="mb-6">
          <p className="text-gray-500 text-xs uppercase tracking-widest mb-1">{selectedCourse?.title}</p>
          <h1 className="font-serif text-2xl font-bold text-white">{activeLesson.title}</h1>
          <p className="text-gray-500 text-xs mt-1">~{activeLesson.duration_mins} minutes</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 mb-6">
          <div className="prose prose-invert max-w-none">
            {activeLesson.content.split('\n\n').map((para: string, i: number) => {
              if (para.startsWith('**') && para.includes('**:')) {
                const [title, ...rest] = para.split('\n')
                return (
                  <div key={i} className="mb-4">
                    <p className="font-semibold text-white text-sm mb-2" dangerouslySetInnerHTML={{ __html: title.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
                    {rest.map((line, j) => <p key={j} className="text-gray-400 text-sm leading-relaxed" dangerouslySetInnerHTML={{ __html: line.replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>') }} />)}
                  </div>
                )
              }
              return (
                <p key={i} className="text-gray-400 text-sm leading-relaxed mb-4" dangerouslySetInnerHTML={{ __html: para.replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>') }} />
              )
            })}
          </div>
        </div>

        {/* Lesson navigation */}
        {courseDetail && (
          <div className="flex items-center justify-between">
            {(() => {
              const lessons = courseDetail.lessons || []
              const currentIdx = lessons.findIndex((l: any) => l.id === activeLesson.id)
              const prev = lessons[currentIdx - 1]
              const next = lessons[currentIdx + 1]
              return (
                <>
                  {prev ? (
                    <button onClick={() => setActiveLesson(prev)} className="text-gray-500 hover:text-white text-sm transition-colors">
                      ← {prev.title}
                    </button>
                  ) : <div />}
                  {next ? (
                    <button onClick={() => setActiveLesson(next)} className="bg-white text-black font-semibold px-5 py-2.5 rounded-xl text-sm hover:bg-gray-100 transition-colors">
                      Next: {next.title} →
                    </button>
                  ) : (
                    <button onClick={() => setQuizMode(true)} className="bg-white text-black font-semibold px-5 py-2.5 rounded-xl text-sm hover:bg-gray-100 transition-colors">
                      Take Quiz →
                    </button>
                  )}
                </>
              )
            })()}
          </div>
        )}
      </div>
    )
  }

  // Course detail view
  if (selectedCourse && courseDetail) {
    const lessons = courseDetail.lessons || []
    return (
      <div className="max-w-3xl mx-auto">
        <button onClick={handleBack} className="text-gray-500 hover:text-white text-sm mb-6 transition-colors">← All courses</button>
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-4xl">{courseDetail.image_emoji}</span>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-xs px-2 py-0.5 rounded-full ${LEVEL_COLORS[courseDetail.level] || 'bg-zinc-800 text-gray-400'}`}>
                  {courseDetail.level}
                </span>
                <span className="text-xs text-gray-600">{courseDetail.category}</span>
              </div>
              <h1 className="font-serif text-2xl font-bold text-white">{courseDetail.title}</h1>
            </div>
          </div>
          <p className="text-gray-400 text-sm leading-relaxed">{courseDetail.description}</p>
          <div className="flex gap-4 mt-3 text-xs text-gray-500">
            <span>📚 {courseDetail.lessons_count} lessons</span>
            <span>⏱ {courseDetail.duration_hours} hours</span>
          </div>
        </div>

        <div className="space-y-2 mb-6">
          <h2 className="text-sm font-medium text-gray-400 uppercase tracking-widest mb-3">Lessons</h2>
          {lessons.map((lesson: any, i: number) => (
            <button
              key={lesson.id}
              onClick={() => setActiveLesson(lesson)}
              className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-4 text-left hover:border-zinc-600 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="w-7 h-7 rounded-full bg-zinc-800 flex items-center justify-center text-xs text-gray-400 flex-shrink-0">
                    {i + 1}
                  </span>
                  <div>
                    <div className="text-white text-sm font-medium">{lesson.title}</div>
                    <div className="text-gray-600 text-xs mt-0.5">{lesson.duration_mins} min</div>
                  </div>
                </div>
                <span className="text-gray-600 text-sm ml-3">→</span>
              </div>
            </button>
          ))}
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 text-center">
          <p className="text-gray-500 text-sm mb-3">Completed all lessons? Test your knowledge.</p>
          <button
            onClick={() => setQuizMode(true)}
            className="bg-white text-black font-semibold px-8 py-2.5 rounded-xl text-sm hover:bg-gray-100 transition-colors"
          >
            Take Quiz ({courseDetail.quiz?.length || 0} questions)
          </button>
        </div>
      </div>
    )
  }

  // Course list
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="font-serif text-2xl font-bold text-white">Legal Education</h1>
        <p className="text-gray-500 text-sm mt-0.5">Learn Indian law through expert courses and quizzes</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {courses.map((course: any) => (
          <button
            key={course.id}
            onClick={() => handleSelectCourse(course)}
            className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 text-left hover:border-zinc-600 transition-colors"
          >
            <div className="text-3xl mb-3">{course.image_emoji}</div>
            <div className="flex items-center gap-2 mb-2">
              <span className={`text-xs px-2 py-0.5 rounded-full ${LEVEL_COLORS[course.level] || 'bg-zinc-800 text-gray-400'}`}>
                {course.level}
              </span>
              <span className="text-xs text-gray-600">{course.category}</span>
            </div>
            <h3 className="font-medium text-white text-sm mb-2">{course.title}</h3>
            <p className="text-gray-500 text-xs leading-relaxed mb-3 line-clamp-2">{course.description}</p>
            <div className="flex gap-3 text-xs text-gray-600">
              <span>📚 {course.lessons_count} lessons</span>
              <span>⏱ {course.duration_hours}h</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
