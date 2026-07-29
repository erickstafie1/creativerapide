// Populeaza sloturile din galerie cu <video> care incarca videos/clip-N.mp4
document.querySelectorAll('#gallery .card').forEach(card => {
  const n = card.dataset.clip;
  const v = document.createElement('video');
  v.src = 'videos/clip-' + n + '.mp4';
  v.poster = 'videos/poster-' + n + '.jpg';
  v.muted = true; v.loop = true; v.playsInline = true; v.preload = 'metadata';
  card.appendChild(v);

  const slot = document.createElement('div');
  slot.className = 'slot';
  slot.innerHTML = '<div class="play">▶</div>';
  card.appendChild(slot);

  // hover preview (mut) doar inainte de pornire; primul click porneste cu sunet + controale,
  // dupa care controalele native (pauza/derulare) functioneaza normal.
  let activated = false;
  card.addEventListener('mouseenter', () => { if(!activated) v.play().catch(()=>{}); });
  card.addEventListener('mouseleave', () => { if(!activated) { v.pause(); v.currentTime = 0; } });
  card.addEventListener('click', () => {
    if (activated) return;            // lasa controalele native sa preia
    activated = true;
    card.classList.add('playing');
    v.muted = false; v.loop = false; v.controls = true;
    v.play().catch(()=>{});
  });
});
