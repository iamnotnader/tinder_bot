`import Ember from 'ember'`

BidAskModalView = Ember.View.extend(
  didInsertElement: ->
    self = this
    $modalContainer = self.$('.bid-ask-center-helper')
    modalOffset = parseFloat($modalContainer.css('top'))

    navbarHeight = parseFloat($('.body__navbar').css('height'))
    modalHeight = $modalContainer.outerHeight()
    initialTopPos = $(window).scrollTop()
    windowHeight = $(window).height()
    $modalContainer.css('margin-top', (initialTopPos + modalOffset) + 'px')
    $(window).scroll([], ->
      currentTopPos = $(window).scrollTop()
      offsetFromBottom = Math.max(modalOffset, windowHeight - modalHeight - modalOffset)
      newInitialTopPos = currentTopPos - modalOffset - modalHeight + windowHeight - offsetFromBottom - modalOffset

      if initialTopPos > currentTopPos
        initialTopPos = Math.max(currentTopPos, 0)
      else if initialTopPos < newInitialTopPos
        initialTopPos = newInitialTopPos

      $modalContainer.css('margin-top', (initialTopPos + modalOffset) + 'px')
    )
)

`export default BidAskModalView`
