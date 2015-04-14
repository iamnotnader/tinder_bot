`import Ember from 'ember'`

ProfileDrilldownView = Ember.View.extend(
  didInsertElement: ->
    self = this
    $modalContainer = self.$('.app__modal-content-container')
    modalOffset = parseFloat($modalContainer.css('top'))

    navbarHeight = parseFloat($('.body__navbar').css('height'))
    modalHeight = $modalContainer.outerHeight()
    initialTopPos = $(window).scrollTop()
    windowHeight = $(window).height()
    lowerBound = initialTopPos
    upperBound = initialTopPos + modalHeight + 2*modalOffset - windowHeight
    $modalContainer.css('margin-top', (initialTopPos + modalOffset) + 'px')
    $(window).scroll([], ->
      currentTopPos = $(window).scrollTop()
      offsetFromBottom = Math.max(modalOffset, windowHeight - modalHeight - modalOffset)
      newInitialTopPos = currentTopPos - modalOffset - modalHeight + windowHeight - offsetFromBottom - modalOffset

      if initialTopPos > currentTopPos
        initialTopPos = Math.max(currentTopPos, 0)
      else if initialTopPos < newInitialTopPos
        initialTopPos = newInitialTopPos

      console.log(modalHeight)
      console.log(initialTopPos + modalOffset)
      console.log(initialTopPos + modalOffset - navbarHeight)
      $modalContainer.css('margin-top', (initialTopPos + modalOffset) + 'px')
    )
)

`export default ProfileDrilldownView`
