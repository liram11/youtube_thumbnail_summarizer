import React, {useEffect, useState} from 'react';
import { Spinner } from './Spinner';
import { useQuery } from '@tanstack/react-query';
import { useQueryClient } from '@tanstack/react-query'

interface ThumbnailSummaryData {
  clickbait_score: number,
  justification: string,
  tldr_of_comments?: string,
  video_summary?: string
}

export interface ClickbaitCheckerProps {
  videoId: string;
  videoType: string;
}

export const ClickbaitChecker: React.FC<ClickbaitCheckerProps> = ({videoId, videoType}) => {
  const [prevVideoId, setPrevVideoId] = useState('')
  const [isActive, setIsActive] = useState(false)
  const queryClient = useQueryClient()

  const { isLoading, error, data } = useQuery<ThumbnailSummaryData>({
    queryKey: ['thumbnailSummary', videoId],
    queryFn: async ({signal}) => {
      const response = await fetch(`http://localhost:5000/api/v1/thumbnail-summary?video_id=${videoId}`, {signal})
      return response.json();
    },
    retry: 5
  })

  useEffect(() => {
    queryClient.cancelQueries({queryKey:['thumbnailSummary', prevVideoId]})

    setPrevVideoId(videoId)
  }, [videoId])


  console.log(error, data)

  if (videoType === 'short') {
    return null
  }

  if (error)  {
    return (
      <div className="clickbait-checker-tooltip-root">
        <div className="clickbait-checker-tooltip">
          X
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="clickbait-checker-tooltip-root">
        <Spinner/>
      </div>
    );
  }

  const {
    clickbait_score,
    justification,
    tldr_of_comments,
    video_summary
  } = data || {}

  return (
    <div className={isActive ? "clickbait-checker-tooltip-root-active" : "clickbait-checker-tooltip-root"} onMouseEnter={() => setIsActive(true)} onMouseLeave={() => setIsActive(false)}>
      {isActive ?
        <div className="clickbait-checker-tooltip">
          <div>
            Clickbait Rating: <span className='clickbait-checker-tooltip-result'>{clickbait_score}/100</span>
          </div>
          <div>
            Justification: <span className='clickbait-checker-tooltip-result'>{justification}</span>
          </div>
          <div>
            TL;DR of Comments: <span className='clickbait-checker-tooltip-result'>{tldr_of_comments ?? ''}</span>
          </div>
          <div>
            Video Summary: <span className='clickbait-checker-tooltip-result'>{video_summary ?? ''}</span>
          </div>
        </div>
        :
        <div className="clickbait-checker-raiting">
          {clickbait_score}
        </div>
      }
    </div>
  )
};
