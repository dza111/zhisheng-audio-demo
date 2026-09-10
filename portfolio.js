// Real portfolio recordings supplied by the team, grouped by service and person.
const portfolioWorks = {
  "recording:dong-zheao": [
    {
      "title": "AOE 干声",
      "src": "/assets/works/recording/dong-zheao/1.mp3"
    },
    {
      "title": "apologize干声",
      "src": "/assets/works/recording/dong-zheao/2.mp3"
    },
    {
      "title": "who am i干声",
      "src": "/assets/works/recording/dong-zheao/3.mp3"
    }
  ],
  "recording:cheng-honglin": [
    {
      "title": "耳机线干声",
      "src": "/assets/works/recording/cheng-honglin/1.mp3"
    },
    {
      "title": "原始股干声",
      "src": "/assets/works/recording/cheng-honglin/2.mp3"
    },
    {
      "title": "原始股干声2",
      "src": "/assets/works/recording/cheng-honglin/3.mp3"
    }
  ],
  "mixing:dong-zheao": [
    {
      "title": "all my love-MIX",
      "src": "/assets/works/mixing/dong-zheao/1.mp3"
    },
    {
      "title": "Get Away-MIX",
      "src": "/assets/works/mixing/dong-zheao/2.mp3"
    },
    {
      "title": "racks on racks  ok1(1)",
      "src": "/assets/works/mixing/dong-zheao/3.mp3"
    }
  ],
  "mixing:cheng-honglin": [
    {
      "title": "nowadays",
      "src": "/assets/works/mixing/cheng-honglin/1.mp3"
    },
    {
      "title": "new song(1)",
      "src": "/assets/works/mixing/cheng-honglin/2.mp3"
    },
    {
      "title": "demo",
      "src": "/assets/works/mixing/cheng-honglin/3.mp3"
    }
  ],
  "arrangement:pm": [
    {
      "title": "juicewrld 136(1)",
      "src": "/assets/works/arrangement/pm/1.mp3"
    },
    {
      "title": "呵呵小样(3)",
      "src": "/assets/works/arrangement/pm/2.mp3"
    },
    {
      "title": "luvme134",
      "src": "/assets/works/arrangement/pm/3.mp3"
    }
  ],
  "arrangement:tai-laoshi": [
    {
      "title": "音频一",
      "src": "/assets/works/arrangement/tai-laoshi/1.mp3"
    },
    {
      "title": "音频二",
      "src": "/assets/works/arrangement/tai-laoshi/2.mp3"
    },
    {
      "title": "音频三",
      "src": "/assets/works/arrangement/tai-laoshi/3.mp3"
    }
  ]
};

function portfolioTracks(kind, id) {
  const works = portfolioWorks[kind + ':' + id];
  if (!works) return [1,2,3].map(i => '<div class="track"><div class="track-info"><strong>作品 ' + i + '</strong><span>试听音频待上传</span></div></div>').join('');
  return works.map(work => `<div class="track portfolio-track"><div class="track-info"><strong>${work.title}</strong><span>作品试听</span></div><audio controls preload="none" aria-label="${work.title}" src="${work.src}"></audio><span class="portfolio-error" role="status" hidden>音频加载失败，请刷新后重试。</span></div>`).join('');
}

// Play only one portfolio sample at a time.
document.addEventListener('play', event => {
  if (!event.target.matches?.('.portfolio-track audio')) return;
  document.querySelectorAll('.portfolio-track audio').forEach(audio => {
    if (audio !== event.target) audio.pause();
  });
}, true);
document.addEventListener('error', event => {
  if (!event.target.matches?.('.portfolio-track audio')) return;
  event.target.parentElement.querySelector('.portfolio-error').hidden = false;
}, true);

