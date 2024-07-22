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
      // const newRoot = document.createElement('div')
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
  if (e.target && hasClass(e.target as HTMLElement | null, 'yt-core-image--loaded')) {
    const videoPreviewContainer = document.getElementById('video-preview-container')
    const target = e.target as HTMLElement
    let videoType = 'video'

    const videoLink = target.parentNode?.parentNode as HTMLLinkElement | null | undefined

    if (!videoLink) {
      console.log('Youtube Clickbait Checker error: no video link found')
      return
    }

    // skipping shorts for now
    if(videoLink.href.indexOf('https://www.youtube.com/shorts/') === 0){
      // hideClickbaitCheckerRoot(videoPreviewContainer)
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
    setTimeout(() => {
      const controlsHost = videoPreviewContainer?.querySelector('.YtInlinePlayerControlsHost')

      if (!controlsHost) {
        console.log('Youtube Clickbait Checker error: controlsHost is not found')
        return
      }

      addClickbaitCheckerRoot({parent: controlsHost, videoId, videoType})
    }, 500)
  }
}, false);

