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
        X
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

  console.log('!!clickbait_score', clickbait_score)

      //       Clickbait Rating: ${clickbait_score}/100
//       Justification: ${justification}
//       TL;DR of Comments: ${tldr_of_comments ?? ''}
//       Video Summary: ${video_summary ?? ''}
  return (
    <div className={isActive ? "clickbait-checker-tooltip-root-active" : "clickbait-checker-tooltip-root"} onMouseEnter={() => setIsActive(true)}>
      <div className="clickbait-checker-raiting">
        {clickbait_score}
      </div>
    </div>
  )
};
