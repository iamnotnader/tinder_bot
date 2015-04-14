`import Ember from 'ember'`

HomeView = Ember.View.extend(
  didInsertElement: ->
    $buttonsContainer = $('.general__left-tab-container')
    navbarHeight = parseFloat($('.body__navbar').css('height'))
    buttonsOffset = parseFloat($buttonsContainer.css('margin-top'))
    $(window).scroll([], ->
      baseTop = Math.max($(window).scrollTop() - navbarHeight, 0)
      $buttonsContainer.css('margin-top', (baseTop + buttonsOffset) + 'px')

      # Disgusting hack we do to make the interval on dashboard-photo components
      # clear when we scroll. For some reason they don't pick up scroll events
      # on their own.
      if window.dashboardPhotoInterval?
        clearInterval(window.dashboardPhotoInterval)
        window.dashboardPhotoInterval = null
    )
)

`export default HomeView`
