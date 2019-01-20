/*! UIkit 3.0.0-rc.11 | http://www.getuikit.com | (c) 2014 - 2018 YOOtheme | MIT License */

(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() :
    typeof define === 'function' && define.amd ? define('uikiticons', factory) :
    (global.UIkitIcons = factory());
}(this, (function () { 'use strict';

    function plugin(UIkit) {

        if (plugin.installed) {
            return;
        }


    }

    if (typeof window !== 'undefined' && window.UIkit) {
        window.UIkit.use(plugin);
    }

    return plugin;

})));
