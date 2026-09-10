const teachingCatalog = {
  recording: {title:'录音课程', intro:'跟随工程师的实际讲解，学习录音的操作与方法。', teachers:['董喆奥','董喆奥','董喆奥']},
  mixing: {title:'混音课程', intro:'通过实际演示，了解混音的制作思路与操作过程。', teachers:['董喆奥','董喆奥','董喆奥','董喆奥','董喆奥']},
  arrangement: {title:'编曲课程', intro:'观看制作人的编曲讲解，探索音乐创作的方法。', teachers:['P.M','P.M','太老师','太老师']}
};
function teachingPage(kind) {
  const course = teachingCatalog[kind];
  return `<main class="shell page teaching-page"><section class="page-title"><div class="eyebrow">ZHISHENG / MUSIC CLASSROOM</div><h1>${course ? course.title : '教学课堂'}</h1><p>${course ? course.intro : '录音、混音与编曲，跟随创作者学习真实的制作过程。'}</p></section><nav class="teaching-tabs" aria-label="课程分类">${Object.entries(teachingCatalog).map(([key,item])=>link('/teaching/'+key,item.title,'btn btn-secondary'+(key===kind?' active':''))).join('')}</nav>${course ? `<section class="teaching-videos">${course.teachers.map((teacher,i)=>`<article class="teaching-video-card"><video controls playsinline preload="none" aria-label="${course.title} · 视频${i+1} · ${teacher}" src="/assets/teaching/${kind}/${i+1}.mp4"></video><div class="teaching-video-info"><h2>${course.title} · 视频 ${i+1}</h2><p>讲解人：${teacher}</p><p class="teaching-video-error" role="status" hidden>视频暂时无法播放，请刷新页面重试。</p></div></article>`).join('')}</section>` : `<section class="teaching-overview">${Object.entries(teachingCatalog).map(([key,item])=>link('/teaching/'+key,`<h2>${item.title}</h2><p>${item.intro}</p><p>${item.teachers.length} 个讲解视频 · ${[...new Set(item.teachers)].join('、')}</p><span class="text-link">进入课程 →</span>`,'teaching-video-card teaching-video-info')).join('')}</section>`}</main>`;
}
document.addEventListener('play', event=>{
  if(!event.target.matches?.('.teaching-video-card video')) return;
  document.querySelectorAll('.teaching-video-card video').forEach(video=>{if(video!==event.target)video.pause();});
},true);
document.addEventListener('error',event=>{
  if(event.target.matches?.('.teaching-video-card video')) event.target.closest('article').querySelector('.teaching-video-error').hidden=false;
},true);

