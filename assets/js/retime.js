/* Re-time a scene to the voiceover without rewriting every tween.
 *
 * Each scene is authored on its own clock ("old" seconds). A scene passes anchors
 * [[old, new], ...] (increasing in both); every tween position is mapped through the
 * piecewise-linear curve they draw, and each duration follows the local tempo
 * (clamped to 0.6×–1.4× so fast moves stay crisp and slow ones don't drag).
 * The same anchors are applied to the scene's timed HTML elements by tools/retime_clips.py.
 *
 *   const tl = hfRetime(gsap.timeline({ paused: true }), ANCHORS);
 *   tl.to(...); tl.fromTo(...); tl.set(...);       // positions in old seconds
 *   window.__timelines["s4"] = tl.raw;
 */
(function () {
  function mapper(a) {
    return function (t) {
      if (t <= a[0][0]) return a[0][1] + (t - a[0][0]);
      for (var i = 1; i < a.length; i++) {
        if (t <= a[i][0]) {
          var k = (t - a[i - 1][0]) / (a[i][0] - a[i - 1][0]);
          return a[i - 1][1] + k * (a[i][1] - a[i - 1][1]);
        }
      }
      var n = a.length - 1;
      return a[n][1] + (t - a[n][0]);
    };
  }
  function scaleVars(v, t, f) {
    if (!v || typeof v !== "object" || typeof v.duration !== "number") return v;
    var slope = (f(t + v.duration) - f(t)) / v.duration;
    var k = Math.min(1.4, Math.max(0.6, slope || 1));
    var out = Object.assign({}, v, { duration: v.duration * k });
    return out;
  }
  window.hfRetimeMap = mapper;
  window.hfRetime = function (tl, anchors) {
    var f = mapper(anchors);
    var api = { raw: tl, map: f };
    ["to", "fromTo", "set"].forEach(function (name) {
      api[name] = function () {
        var args = Array.prototype.slice.call(arguments);
        var last = args.length - 1;
        if (typeof args[last] === "number") {
          var t = args[last];
          args[last] = f(t);
          var vi = name === "fromTo" ? 2 : 1;
          if (name !== "set") args[vi] = scaleVars(args[vi], t, f);
        }
        tl[name].apply(tl, args);
        return api;
      };
    });
    return api;
  };
})();
