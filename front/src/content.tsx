const CLICKBAIT_CHECKER_ROOT_CLASS = 'clickbait_checker_root'

function hasClass(elem: HTMLElement | null, className: string) {
  return elem?.classList.contains(className);
}

interface ThumbnailSummaryData {
  clickbait_score: number,
  justification: string,
  tldr_of_comments?: string,
  video_summary?: string
}

async function addClickbaitCheckerRoot({parent, videoId}: {parent: ParentNode | HTMLElement | null, videoId: string}) {
  let root = parent?.querySelector(`.${CLICKBAIT_CHECKER_ROOT_CLASS}`) as HTMLDivElement
  if (parent && !root) {
    if(!root)  {
      root = document.createElement('div')
    }


    let data = {} as ThumbnailSummaryData
    try {
      const response = await fetch(`http://localhost:5000/api/v1/thumbnail-summary?video_id=${videoId}`)

      if (!response.ok) {
        console.log('failed to fetch thumbnail summary')
        return
      }

      data = await response.json() as ThumbnailSummaryData

    } catch (e) {
      console.log('failed to fetch thumbnail summary', e)
      return
    }

    console.log('data', data)

    const {
      clickbait_score,
      justification,
      tldr_of_comments,
      video_summary
    } = data

    const tooltipText = `
      Clickbait Rating: ${clickbait_score}/100
      Justification: ${justification}
      TL;DR of Comments: ${tldr_of_comments ?? ''}
      Video Summary: ${video_summary ?? ''}
    `

    root.innerHTML = tooltipText
    root.classList.add(CLICKBAIT_CHECKER_ROOT_CLASS)
    parent?.appendChild(root)
    return root
  }
}

function hideClickbaitCheckerRoot(parent: ParentNode | HTMLElement | null) {
  const root = parent?.querySelector(`.${CLICKBAIT_CHECKER_ROOT_CLASS}`) as HTMLDivElement
  if (parent && root) {
    root.style.display = 'none'

    return root
  }
}

document.addEventListener('mouseover', (e) => {
  if (e.target && hasClass(e.target as HTMLElement | null, 'yt-core-image--loaded')) {
    const videoPreviewContainer = document.getElementById('video-preview-container')
    const target = e.target as HTMLElement

    const videoLink = target.parentNode?.parentNode as HTMLLinkElement | null | undefined

    if (!videoLink) {
      console.log('no video link found')
      return
    }

    // skipping shorts for now
    if(videoLink.href.indexOf('https://www.youtube.com/shorts/') === 0){
      hideClickbaitCheckerRoot(videoPreviewContainer)
      return
      // videoId = videoLink.href.replace('https://www.youtube.com/shorts/', '')
    }

    const params = new URL(videoLink.href).searchParams;
    const videoId = params.get("v") || '';

    if(!videoId) {
      console.log('no video id found')
      return
    }

    // wait until controlsHost is loaded
    setTimeout(() => {
      const controlsHost = videoPreviewContainer?.querySelector('.YtInlinePlayerControlsHost')

      if (!controlsHost) {
        console.log('controlsHost is not found')
        return
      }

      console.log(controlsHost)
      addClickbaitCheckerRoot({parent: controlsHost, videoId})
    }, 300)


    console.log('tooltip added')
  }
}, false);

