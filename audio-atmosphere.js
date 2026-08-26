(() => {
  const canvas = document.querySelector('#audio-atmosphere');
  if (!canvas) return;

  const ctx = canvas.getContext('2d', { alpha: true });
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const particles = [];
  const cloudGrains = [];
  let width = 0;
  let height = 0;
  let ratio = 1;
  let animationFrame = 0;
  let lastFrame = 0;

  function randomParticle() {
    return {
      x: Math.random(),
      y: Math.random(),
      radius: Math.random() * 1.25 + 0.2,
      alpha: Math.random() * 0.44 + 0.1,
      speed: Math.random() * 0.018 + 0.004,
      phase: Math.random() * Math.PI * 2
    };
  }

  function resize() {
    ratio = Math.min(window.devicePixelRatio || 1, 1.5);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);

    particles.length = 0;
    const count = Math.max(260, Math.min(780, Math.round((width * height) / 1900)));
    for (let index = 0; index < count; index += 1) particles.push(randomParticle());
    cloudGrains.length = 0;
    const cloudCount = Math.max(340, Math.min(920, Math.round((width * height) / 1500)));
    for (let index = 0; index < cloudCount; index += 1) {
      cloudGrains.push({
        progress: Math.random(),
        lane: Math.random() > .45 ? 0 : 1,
        spread: (Math.random() - .5) * 2,
        phase: Math.random() * Math.PI * 2,
        size: Math.random() * 1.55 + .25,
        alpha: Math.random() * .42 + .09
      });
    }
    draw(0, true);
  }

  function drawParticleField(time, still) {
    particles.forEach(particle => {
      const shimmer = still ? 0.6 : 0.45 + Math.sin(time * 0.0012 + particle.phase) * 0.3;
      const driftX = still ? 0 : Math.sin(time * 0.00014 + particle.phase) * 0.018;
      const driftY = still ? 0 : time * particle.speed * 0.00003;
      const x = ((particle.x + driftX + 1) % 1) * width;
      const y = ((particle.y + driftY + 1) % 1) * height;
      ctx.beginPath();
      ctx.fillStyle = `rgba(255,255,255,${particle.alpha * shimmer})`;
      ctx.arc(x, y, particle.radius, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  function wavePoint(x, time, offset, amplitude) {
    const progress = x / Math.max(width, 1);
    return height * offset
      + Math.sin(progress * 7.8 + time * 0.00023) * amplitude
      + Math.sin(progress * 15.4 - time * 0.00015) * amplitude * 0.26;
  }

  function drawBand(time, offset, amplitude, thickness, alpha) {
    const gradient = ctx.createLinearGradient(0, 0, width, 0);
    gradient.addColorStop(0, 'rgba(255,255,255,0)');
    gradient.addColorStop(0.17, `rgba(255,255,255,${alpha * 0.62})`);
    gradient.addColorStop(0.5, `rgba(255,255,255,${alpha})`);
    gradient.addColorStop(0.82, `rgba(255,255,255,${alpha * 0.54})`);
    gradient.addColorStop(1, 'rgba(255,255,255,0)');

    ctx.beginPath();
    for (let x = -30; x <= width + 30; x += 16) {
      const y = wavePoint(x, time, offset, amplitude);
      if (x < 0) ctx.moveTo(x, y - thickness); else ctx.lineTo(x, y - thickness);
    }
    for (let x = width + 30; x >= -30; x -= 16) ctx.lineTo(x, wavePoint(x, time, offset, amplitude) + thickness);
    ctx.closePath();
    ctx.filter = 'blur(25px)';
    ctx.fillStyle = gradient;
    ctx.fill();
    ctx.filter = 'none';

    ctx.globalAlpha = .68;
    ctx.beginPath();
    for (let x = -30; x <= width + 30; x += 16) {
      const y = wavePoint(x, time, offset, amplitude);
      if (x < 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = gradient;
    ctx.lineWidth = Math.max(1, thickness * .095);
    ctx.shadowBlur = 28;
    ctx.shadowColor = 'rgba(255,255,255,.72)';
    ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.globalAlpha = 1;
  }

  function drawCloudGrains(time, still) {
    cloudGrains.forEach(grain => {
      const lane = grain.lane === 0 ? { offset:.28, amplitude:Math.min(118, height * .145), thickness:Math.min(118, height * .14) } : { offset:.43, amplitude:Math.min(96, height * .115), thickness:Math.min(86, height * .1) };
      const progress = still ? grain.progress : ((grain.progress + time * 0.000012 * (grain.lane ? -.7 : 1)) % 1 + 1) % 1;
      const x = progress * width;
      const center = wavePoint(x, time, lane.offset, lane.amplitude);
      const oscillation = Math.sin(time * .00065 + grain.phase) * lane.thickness * .09;
      const y = center + grain.spread * lane.thickness * .7 + oscillation;
      const taper = Math.max(0, 1 - Math.abs(grain.spread) * .42);
      const twinkle = still ? .65 : .52 + Math.sin(time * .0014 + grain.phase) * .33;
      ctx.beginPath();
      ctx.fillStyle = `rgba(255,255,255,${grain.alpha * taper * twinkle})`;
      ctx.arc(x, y, grain.size * (1 + taper * .45), 0, Math.PI * 2);
      ctx.fill();
    });
  }

  function draw(time, still = false) {
    ctx.clearRect(0, 0, width, height);
    const vignette = ctx.createRadialGradient(width * .5, height * .43, 0, width * .5, height * .43, Math.max(width, height) * .72);
    vignette.addColorStop(0, 'rgba(255,255,255,.055)');
    vignette.addColorStop(.46, 'rgba(120,120,120,.02)');
    vignette.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = vignette;
    ctx.fillRect(0, 0, width, height);
    drawParticleField(time, still);
    drawBand(time, .27, Math.min(128, height * .16), Math.min(120, height * .15), .83);
    drawBand(time + 1600, .43, Math.min(102, height * .12), Math.min(88, height * .105), .56);
    drawBand(time + 3800, .59, Math.min(76, height * .09), Math.min(56, height * .07), .24);
    drawCloudGrains(time, still);
  }

  function loop(time) {
    if (time - lastFrame > 32) {
      draw(time);
      lastFrame = time;
    }
    animationFrame = requestAnimationFrame(loop);
  }

  function start() {
    cancelAnimationFrame(animationFrame);
    if (reducedMotion.matches) draw(0, true);
    else animationFrame = requestAnimationFrame(loop);
  }

  resize();
  start();
  window.addEventListener('resize', resize, { passive: true });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) cancelAnimationFrame(animationFrame); else start();
  });
  reducedMotion.addEventListener?.('change', start);
})();
