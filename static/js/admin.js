/* 목록의 노출 버튼 — equipment/admin_toggle.py 참고.

   버튼 한 번이 곧 한 번의 저장이다. 눌린 동안은 다시 눌리지 않게 잠그고,
   실패하면 원래 모양으로 되돌린 뒤 알린다 — 화면만 바뀌고 실제로는 안 바뀐
   상태가 남는 것이 이 버튼을 만든 이유이기 때문이다. */
(function () {
  'use strict';

  function csrfToken() {
    var m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.wj-toggle');
    if (!btn || btn.disabled) return;
    e.preventDefault();

    var url = btn.dataset.toggleUrl;
    if (!url) return;

    var previousText = btn.textContent;
    var wasOff = btn.classList.contains('is-off');
    btn.disabled = true;
    btn.textContent = '바꾸는 중…';

    fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': csrfToken(),
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
      .then(function (res) {
        if (!res.ok) throw new Error(res.status);
        return res.json();
      })
      .then(function (data) {
        btn.classList.toggle('is-off', !data.active);
        btn.textContent = data.label;
        btn.disabled = false;
      })
      .catch(function () {
        btn.classList.toggle('is-off', wasOff);
        btn.textContent = previousText;
        btn.disabled = false;
        window.alert('바꾸지 못했습니다. 새로고침한 뒤 다시 눌러주세요.');
      });
  });
})();
