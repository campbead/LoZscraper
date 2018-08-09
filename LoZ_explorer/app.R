#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)

library(dplyr)
library(ggplot2)
library(grid)
library(gridExtra)

room_data <- read.csv("../data/fixed_room_data.csv")
room_order <- read.csv("../data/unique_room_list_double_hundo_with_index.csv", header = FALSE, col.names = c('Number','Room'))

room_list <- unique(room_data$Room)

# Define UI for application that draws a histogram
ui <- fluidPage(
   
  # Application title
  titlePanel("Room histogram"),
   
  # Sidebar with a slider input for number of bins 
  sidebarLayout(
    sidebarPanel(
      selectInput("room", "Room:", 
                  choices=room_list),
        hr(),
        #helpText("Pick a room"),
      sliderInput('bin_size', 'Bin size (s):', 
                  min = 0.1, max = 1, step = 0.1, value = 0.5
      )
      ),

    # Show a plot of the generated distribution
    mainPanel(
      
      plotOutput("roomHist")
    )
    
  )
    
)

# Define server logic required to draw a histogram
server <- function(input, output) {
   
    # filter out the data you need
    durations_for_rooms <- reactive({ 
      room_data %>%
      filter(Room == input$room) %>%
      select(Duration) %>%
      na.omit() 
    })
    # create your super cool label
    the_label <- reactive ({ 
      paste("Duration of", input$room ,"(seconds)")
    })
    
    # pick the color based on overworld or dungeon
    bar_color <- reactive({
      if (substr(input$room, start = 2, stop = 2) == 'O') {
        'green4'
      } else {
        'navyblue'  
        }
      
    })
    
  
    
    # make your gg plot
    output$roomHist <- renderPlot({
      
      
      ggplot(durations_for_rooms(), aes(x = Duration) ) + 
      geom_histogram(binwidth = input$bin_size,
                     fill = bar_color(),
                     position="identity",
                     alpha= 0.8) + 
                     xlab(the_label())+
      geom_vline(aes(xintercept =median(Duration)), col = 'darkred', size=1.5)
    })
}

# Run the application 
shinyApp(ui = ui, server = server)

