'use strict';

var exports = {}

var moveTo = function moveTo(list, fromIndex, toIndex) {
  var arr = [];
  toIndex = ~ ~toIndex;
  fromIndex = ~ ~fromIndex;
  if (toIndex >= fromIndex) {
    arr = arr.concat(list.slice(0, fromIndex)).concat(list.slice(fromIndex + 1, toIndex + 1)).concat(list.slice(fromIndex, fromIndex + 1)).concat(list.slice(toIndex + 1));
  } else {
    arr = arr.concat(list.slice(0, toIndex)).concat(list.slice(fromIndex, fromIndex + 1)).concat(list.slice(toIndex, fromIndex)).concat(list.slice(fromIndex + 1));
  }
  return arr;
};

var confirmTarget = function confirmTarget(target) {
  return target.nodeName === 'TD' ? target.parentElement : target;
};

var workWithClass = function workWithClass(element, newClass, defaultClassName, doWhat) {
  if (!element.classList) return;
  var className = defaultClassName;
  if (newClass) className = newClass;
  if (doWhat === 'add') {
    element.classList.add(className);
  } else if (doWhat === 'remove') {
    element.classList.remove(className);
  }
};

exports.install = function (Vue) {
  Vue.directive('dragable', {
    params: ['drag-class'],
    bind: function bind() {
      var self = this;
      var element = this.el;
      element.draggable = true;
      element.ondragstart = function (event) {
        workWithClass(element, self.params['dragClass'], 'yita-draging', 'add');
        event.dataTransfer.setData('text', self._scope['$index']);
      };
      element.ondragend = function (event) {
        workWithClass(element, self.params['dragClass'], 'yita-draging', 'remove');
      };
      element.ondrag = function (event) {};
    },
    update: function update(newValue, oldValue) {},
    unbind: function unbind() {}
  });
  Vue.directive('droper', {
    params: ['drag-class'],
    twoWay: true,
    bind: function bind() {
      var self = this;
      var expr = this.expression;
      var element = this.el;
      element.ondragenter = function (event) {
        var target = event.target;
        target = confirmTarget(target);
        // let index = Array.from(this.children).indexOf(target)
        workWithClass(target, self.params['dragClass'], 'yita-draging-zone', 'add');
      };
      element.ondragleave = function (event) {
        var target = event.target;
        target = confirmTarget(target);
        workWithClass(target, self.params['dragClass'], 'yita-draging-zone', 'remove');
      };
      element.ondragover = function (event) {
        event.preventDefault();
      };
      element.ondrop = function (event) {
        event.preventDefault();
        event.stopPropagation();
        var fromIndex = event.dataTransfer.getData('text');
        var target = event.target;
        target = confirmTarget(target);
        workWithClass(target, self.params['dragClass'], 'yita-draging-zone', 'remove');
        var toIndex = Array.from(this.children).indexOf(target);
        if (toIndex === -1) {
          console.warn('cannot found', target, 'in ', this);
        }
        var out = moveTo(self.vm[expr], fromIndex, toIndex);
        self.vm.$set(expr, out);
      };
    },
    update: function update(value, oldValue) {},
    unbind: function unbind() {}
  });
};

Vue.use(exports);
