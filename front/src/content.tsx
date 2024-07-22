
const CLICKBAIT_CHECKER_ROOT_CLASS = 'clickbait_checker_root'

function hasClass(elem: HTMLElement | null, className: string) {
  return elem?.classList.contains(className);
}

function addClickbaitCheckerRoot(parent: ParentNode | HTMLElement | null) {
  const root = parent?.querySelector(`.${CLICKBAIT_CHECKER_ROOT_CLASS}`) as HTMLDivElement
  if (parent && !root) {
    const  newRoot = document.createElement('div')


    newRoot.innerHTML = 'tooltip'
    parent?.appendChild(newRoot)
    console.log('render react')
    return newRoot
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
      addClickbaitCheckerRoot(controlsHost)
    }, 300)


    console.log('tooltip added')
  }
}, false);

