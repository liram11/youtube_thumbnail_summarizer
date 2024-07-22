import React from 'react'
import { createRoot } from "react-dom/client";
import { ClickbaitChecker } from "./components/ClickbaitChecker";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const CLICKBAIT_CHECKER_ROOT_CLASS = 'clickbait-checker-root'
const queryClient = new QueryClient()

function hasClass(elem: HTMLElement | null, className: string) {
  return elem?.classList.contains(className);
}


function addClickbaitCheckerRoot({parent, videoId, videoType}: {parent: ParentNode | HTMLElement | null, videoId: string, videoType:string}) {
  const root = parent?.querySelector(`.${CLICKBAIT_CHECKER_ROOT_CLASS}`) as HTMLDivElement
  if (parent) {
    let newRoot = document.createElement('div')
    if (root) {
      newRoot = root
    } else {
      newRoot.classList.add(CLICKBAIT_CHECKER_ROOT_CLASS)
      parent?.appendChild(newRoot)
    }

    const reactRoot = createRoot(newRoot)
    reactRoot.render(
      <QueryClientProvider client={queryClient}>
        <ClickbaitChecker videoId={videoId} videoType={videoType}/>
      </QueryClientProvider>
    );

    return newRoot
  }
}

document.addEventListener('mouseover', (e) => {
  const target = e.target as HTMLElement | null
  const isThumbnail = target && hasClass(target, 'yt-core-image--loaded')
  const isDetails = target?.matches('#details, #details *')

  if (target && (isThumbnail || isDetails)) {
    const videoPreviewContainer = document.getElementById('video-preview-container')

    let videoType = 'video'

    let videoLink = target.parentNode?.parentNode as HTMLLinkElement | null | undefined

    if (isDetails) {
      videoLink = videoPreviewContainer?.querySelector('#media-container-link') as HTMLLinkElement | null | undefined
    }

    if (!videoLink || !videoLink.href) {
      console.log('Youtube Clickbait Checker error: no video id found')
      return
    }

    // skipping shorts for now
    if(videoLink.href.indexOf('https://www.youtube.com/shorts/') === 0){
      videoType = 'short'
      return
      // videoId = videoLink.href.replace('https://www.youtube.com/shorts/', '')
    }

    const params = new URL(videoLink.href).searchParams;
    const videoId = params.get("v") || '';

    if(!videoId) {
      console.log('Youtube Clickbait Checker error: no video id found')
      return
    }

    // wait until controlsHost is loaded

    const controlsHost = videoPreviewContainer?.querySelector('.YtInlinePlayerControlsHost')

    if (!controlsHost) {
      console.log('Youtube Clickbait Checker error: controlsHost is not found')
      return
    }

    addClickbaitCheckerRoot({parent: controlsHost, videoId, videoType})

  }
}, false);

