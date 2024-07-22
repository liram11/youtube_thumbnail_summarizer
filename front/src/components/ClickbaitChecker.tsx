import React, {useEffect, useRef, useState} from 'react';
import { Spinner } from './Spinner';
import { useQuery } from '@tanstack/react-query';
import { useQueryClient } from '@tanstack/react-query'

interface ThumbnailSummaryData {
  clickbait_score: number,
  justification: string,
  tldr_of_comments?: string,
  video_summary?: string,
  video_id: string
}

// const API_HOST = 'https://9ec9f617-5931-44bb-a369-34055cbc23b4-00-1ysli21nuv1di.pike.replit.dev'
const API_HOST = ' http://127.0.0.1:5000'

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
      const response = await fetch(`${API_HOST}/api/v1/thumbnail-summary?video_id=${videoId}`, {signal})
      return response.json();
    },
    retry: 5
  })

  useEffect(() => {
    queryClient.cancelQueries({queryKey:['thumbnailSummary', prevVideoId]})

    setPrevVideoId(videoId)
  }, [videoId])

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


  const {
    clickbait_score,
    justification,
    tldr_of_comments,
    video_summary,
    video_id
  } = data || {}

  if (isLoading || videoId !== video_id) {
    return (
      <div className="clickbait-checker-tooltip-root" onMouseEnter={() => setIsActive(true)} onMouseLeave={() => setIsActive(false)}>
        <Spinner/>
      </div>
    );
  }

  return (
    <div className={isActive ? "clickbait-checker-tooltip-root-active" : "clickbait-checker-tooltip-root"} onMouseEnter={() => setIsActive(true)} onMouseLeave={() => setIsActive(false)}>
      {isActive ?
        <div className="clickbait-checker-tooltip">
          <div className="clickbait-checker-tooltip-result">
            <span className='clickbait-checker-tooltip-result-title'>Clickbait Rating: </span>{clickbait_score}/100
          </div>
          <div className="clickbait-checker-tooltip-result">
            <span className='clickbait-checker-tooltip-result-title'>Justification: </span>{justification}
          </div >
          <div className="clickbait-checker-tooltip-result">
            <span className='clickbait-checker-tooltip-result-title'>TL;DR of Comments: </span>{tldr_of_comments ?? ''}
          </div>
          <div className="clickbait-checker-tooltip-result">
            <span className='clickbait-checker-tooltip-result-title'>Video Summary: </span>{video_summary ?? ''}
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
