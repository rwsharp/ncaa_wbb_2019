# http://www.sports-reference.com/cbb/

# set some constants
tau <- 4.26
sig <- 11 
h   <- 4

# code to compute the probability that one team is better than another based on point spread, x.
# compute P(Z>0 | X=x) from eq. (12) pnorm(2*tau^2/(sig*sqrt((sig^2+2*tau^2)*(sig^2+4*tau^2)))*x - h/sig*sqrt((sig^2+4*tau^2)/(sig^2+2*tau^2))) 
a <- 2*tau^2/(sig*sqrt((sig^2+2*tau^2)*(sig^2+4*tau^2)))
b <- 2*tau^2*h/(sig*sqrt((sig^2+2*tau^2)*(sig^2+4*tau^2)))

x <- 20
pnorm(a*x-b)

###################

# include XML package to read data from HTML tables
library(XML)

# Set up teams list: include top 200 by RPI

# Get top 68 teams
url <- "http://www.cbssports.com/collegebasketball/rankings/rpi/index1"
tables <- readHTMLTable(url)

# get teams 1-34
teams <- tables[[4]]
names(teams) <- sapply(teams[1,], as.character)
teams <- teams[-1,]

# get teams 35-68
teams2 <- tables[[5]]
names(teams2) <- sapply(teams2[1,], as.character)
teams2 <- teams2[-1,]

# Get remaining teams
url <- "http://www.cbssports.com/collegebasketball/rankings/rpi/index2"
tables <- readHTMLTable(url)

# skip first row for formatting reasons
teams3 <- tables[[4]]
names(teams3) <- sapply(teams3[1,], as.character)
teams3 <- teams3[2:nrow(teams3),]

teams4 <- tables[[5]]
names(teams4) <- sapply(teams4[1,], as.character)
teams4 <- teams4[2:nrow(teams4),]

teams <- rbind(teams, teams2, teams3, teams4)

# Grand Canyon university joind D1 in 2014, so remove it for 2013 testing
id = which(teams$School == "Grand Canyon")
teams$School[id]
teams = teams[-id,]

# Incarnate Word university joind D1 in 2014, so remove it for 2013 testing
id = which(teams$School == "Incarnate Word")
teams$School[id]
teams = teams[-id,]

# regularize team names
# all lower case
# replace white space with '-'
for(i in 1:length(teams$School)) {
  name <- teams$School[i]
  url.name <- gsub("&", "", gsub(" ", "-", tolower(as.character(name))))
  teams$url.name[i] <- url.name
  url <- paste("http://www.sports-reference.com/cbb/schools/",url.name, sep="")
}

# make some team url corrections by hand
transformName1 <- function(name) {
  pairs <- c(
    "Miami (Fla.)","miami-fl",
    "St. Mary's","saint-marys-ca",
    "Southern Miss","southern-mississippi",
    "Ole Miss","mississippi",
    "Stephen F. Austin","stephen-f-austin",
    "Detroit","detroit-mercy",
    "Saint Joseph's","saint-josephs",
    "Mount St. Mary's","mount-st-marys",
    "St. John's","st-johns-ny",
    "Loyola-Maryland","loyola-md",
    "St. Bonaventure","st-bonaventure",
    "Albany","albany-ny",
    "Bryant University","bryant",
    "LIU-Brooklyn","long-island-university",
    "St. Francis (N.Y.)","st-francis-ny",
    "NC-Asheville","north-carolina-asheville",
    "Loyola-Chicago","loyola-il",
    "Northridge","cal-state-northridge",
    "Santa Barbara","california-santa-barbara",
    "Bowling Green","bowling-green-state",
    "William & Mary","william-mary",
    "Miami (Ohio)","miami-oh",
    "E. Tennessee State","east-tennessee-state",
    "Texas State-San Marcos","texas-state",
    "St. Peter's","saint-peters",
    "New Jersey Tech","njit",
    "NC-Wilmington","north-carolina-wilmington",
    "SIU-Edwardsville","southern-illinois-edwardsville",
    "Wisconsin-Milwaukee","milwaukee",
    "St. Francis (Pa.)","saint-francis-pa",
    "Prairie View A&M","prairie-view",
    "NC-Greensboro","north-carolina-greensboro",
    "The Citadel","citadel")
  
  n <- length(pairs)
  full.name <- pairs[seq(1,n,2)]
  url.name  <- pairs[seq(2,n,2)]
  
  idx <- which(full.name == name)
  if(length(idx) > 0) {
    return(url.name[idx])
  } else {
    return("")
  }
}

# some team url corrections
transformName2 <- function(name) {
  
  pairs <- c(   
    "Albany (NY)", "albany-ny",
    "Missouri-Kansas City", "missouri-kansas-city",
    "Alabama-Birmingham", "uab",         
    "Nevada-Las Vegas", "unlv",           
    "Miami (FL)", "miami-fl",                  
    "Loyola (IL)", "loyola-il",                
    "Lafayette", "lafayette",            
    "Texas A&M", "texas-am",                  
    "Louisiana State", "lsu",     
    "West Virginia", "west-virginia",    
    "Texas Christian", "tcu",
    "St. John's (NY)", "st-johns-ny",            
    "Alabama A&M", "alabama-am",              
    "Miami (OH)", "miami-oh",  
    "Central Florida", "central-florida",    
    "Loyola (MD)", "loyola-md",            
    "Saint Mary's (CA)", "saint-marys-ca", 
    "North Carolina A&T", "north-carolina-at",
    "Saint Francis (PA)", "saint-francis-pa",
    "Saint Peter's", "saint-peters",
    "Grambling", "grambling",
    "Virginia Military Institute", "vmi",
    "Texas A&M-Corpus Christi", "texas-am-corpus-christi",   
    "St. Francis (NY)", "st-francis-ny",
    "Florida A&M", "florida-am",
    "William & Mary","william-mary",
    "Stephen F. Austin","stephen-f-austin",
    "St. Bonaventure","st-bonaventure",
    "Saint Joseph's","saint-josephs",
    "Mount St. Mary's","mount-st-marys",
    "Central Florida", "ucf"
    )
  
  n <- length(pairs)
  full.name <- pairs[seq(1,n,2)]
  url.name  <- pairs[seq(2,n,2)]
  
  idx <- which(full.name == name)
  if(length(idx) > 0) {
    return(url.name[idx])
  } else {
    return("")
  }
}


n <- nrow(teams)

for(i in 1:n) {
  name <- teams$School[i]
  url.name <- transformName1(name)
  if(url.name != "") {
    teams$url.name[i] <- url.name
  }
}

t <- matrix(0,n,n)
teams$ngames <- array(0, n)


## test code for verifying urls
## loop through all teams on the teams list
#bad.teams <- c()
#bad.home <- c()
#for(teams.idx in 1:n) {
#  
#  # read in team game results
#  team1.name <- teams$url.name[teams.idx]
#  url <- paste("http://www.sports-reference.com/cbb/schools/",team1.name, sep="")
#  url <- paste(url, "/2013-schedule.html", sep="")
#  tables <- readHTMLTable(url)
#  
#  outcomes <- tables[[length(tables)]]
#  if(ncol(outcomes) != 13) {
#    print("error")
#    break
#  }
#  
#  for(games.idx in 1:nrow(outcomes)) {
#
#    # skip non D1 games
#    if(outcomes$Conf[games.idx] == "") {
#      next
#    }
#    
#    team2 <- outcomes$Opponent[games.idx]
#    
#    team2.name <- transformName2(team2)
#    if(team2.name == "") {
#      team2.name <- gsub(" ", "-", tolower(as.character(team2)))
#    }  
#    
#    team.index <- which(teams$url.name == team1.name)
#    opponent.index <- which(teams$url.name == team2.name)
#    if(length(opponent.index) == 0) {
#      bad.teams <- c(bad.teams, as.character(team2))
#      bad.home <- c(bad.home, as.character(team1.name))
#    }
#  }
#}
#
#unique(bad.teams)

ncaa.team1  <- c()
ncaa.team2  <- c()
ncaa.winner <- c()

# loop through all teams on the teams list
for(teams.idx in 1:n) {
  
  # read in team game results
  team1.name <- teams$url.name[teams.idx]
  url <- paste("http://www.sports-reference.com/cbb/schools/",team1.name, sep="")
  url <- paste(url, "/2013-schedule.html", sep="")
  tables <- readHTMLTable(url)
  
  print(c(teams.idx, team1.name))
  
  outcomes <- tables[[length(tables)]]
  if(ncol(outcomes) != 13) {
    print("error")
    break
  }
  outcomes$Tm <- as.numeric(as.character(outcomes$Tm))
  outcomes$Opp <- as.numeric(as.character(outcomes$Opp))  
  
  # note that the paper is inconsistent with the indexing convention
  # if game is held at home court i
  # observe i vs. j (i=home, j=away, margin is x_ij = home.points - away.points)
  # increment N_i by 1
  # increment N_j by 1
  # probability that home is better than away r_x(g(i,j)) = pnorm(a*spread-b)
  # intuition: if home wins big, r > 50% and votes prefer to go from j to i
  # probability of transfer from i to j increased by t_ij += 1 - r_x
  # probability of transfer from j to i increased by t_ji += r_x
  # probability of transfer from i to i increased by t_ii += r_x
  # probability of transfer from j to j increased by t_jj += 1 - r_x
  # 
  # if game is held at neutral court, adjust spread by h
  # let team1 = i and team2 = j, adjust spread as if game were played at home by team1
  # observe i vs. j (i=team1, j=team2, margin is x_ij = team1.points - team2.points + h)
  # update as if team1 = home and team2 = away
  
  for(games.idx in 1:nrow(outcomes)) {
    
    # skip non D1 games
    if(outcomes$Conf[games.idx] == "") {
      next
    }
    
    team2 <- outcomes$Opponent[games.idx]
    #team2.name <- gsub(" ", "-", tolower(as.character(team2)))
    team2.name <- transformName2(team2)
    if(team2.name == "") {
      team2.name <- gsub(" ", "-", tolower(as.character(team2)))
    }  
    
    team.index <- which(teams$url.name == team1.name)
    opponent.index <- which(teams$url.name == team2.name)

    if(outcomes$Type[games.idx] == "NCAA") {
      # if it's a tournamet game, record the outcome
      if(length(opponent.index) > 0) {
        if(team.index < opponent.index) {
          ncaa.team1 <- c(ncaa.team1, as.character(teams$url.name[teams.idx]))
          ncaa.team2 <- c(ncaa.team2, as.character(team2.name))
          print(c("NCAA>>>>>> ", team1.name, team2.name))
          if(outcomes$Tm[games.idx] > outcomes$Opp[games.idx]) {
            ncaa.winner <- c(ncaa.winner, 1)
          } else {
            ncaa.winner <- c(ncaa.winner, 2)
          }
        }
      }
      
      # exclude the game from the rankings calculation
      next
    }
    
    
    if(length(opponent.index) > 0) {

      # don't double count...
      if(opponent.index < team.index) {
        # in this case the game in question was already recorded when the other team was team1, so skip it
        # print(paste("skipping",paste(team1.name,paste("vs.",team2.name))))
        next
      }
      
      # compute margin of victory for the home team
      if(as.character(outcomes[games.idx,4]) == "") {
        team.home <- team1.name
        team.away <- team2.name
        i <- team.index
        j <- opponent.index
        if(outcomes$OT[games.idx] == "OT") {
          spread <- 0
        } else {
          spread <- outcomes$Tm[games.idx] - outcomes$Opp[games.idx]
        }
      } else if(as.character(outcomes[games.idx,4]) == "@") {
        team.home <- team2.name
        team.away <- team1.name
        i <- opponent.index
        j <- team.index
        if(outcomes$OT[games.idx] == "OT") {
          spread <- 0
        } else {
          spread <- outcomes$Opp[games.idx] - outcomes$Tm[games.idx]
        }
      } else {
        # neutral court, adjust spread as if team1 played at home
        team.home <- team1.name
        team.away <- team2.name
        i <- team.index
        j <- opponent.index
        if(outcomes$OT[games.idx] == "OT") {
          spread <- h
        } else {
          spread <- outcomes$Tm[games.idx] - outcomes$Opp[games.idx] + h
        }
      }
    
      if(is.na(spread)) {
        next # resolves problem when a game is listed online before a score is available
      }
      
      teams$ngames[i] <- teams$ngames[i] + 1
      teams$ngames[j] <- teams$ngames[j] + 1
  
      # update the probability matrix: t[i,j] = probability that i is a better team than j
      r <- pnorm(a*spread-b)
      t[i,j] <- t[i,j] + (1-r)
      t[j,i] <- t[j,i] + r
      t[i,i] <- t[i,i] + r
      t[j,j] <- t[j,j] + (1-r)
      
      #print(paste(paste(paste(team.home,"vs."), team.away),paste(spread,r)))
  
      } 
  }

}

# normalize
for(i in 1:n) {
  if(teams$ngames[i]>0)
  t[i,] <- t[i,]/teams$ngames[i]
}

#initialize ranking procedure
p <- matrix(1/n, 1, n)

for(i in 1:n) {
  p[i] <- n-i+1
}

p <- p/sum(p)

# run ranking procedure
for(i in 1:1000) {
  p.next <- p %*% t
  if(i %% 100 == 0) {
    print(norm(p.next - p))
  }
  p <- p.next
}

# add LRMC score to table and sort to get ranking
teams$LRMC.score <- t(p)

teams <- teams[order(teams$LRMC.score, decreasing=TRUE),]

teams.alpha <- teams[order(teams$School, decreasing=FALSE),]

# for each matchup in the NCAA Tournement, compute the number of
# times the LRMC model predicted the winner.
correct <- 0
total <- length(ncaa.team1)
for(i in 1:total) {
  
  score1 <- teams$LRMC.score[teams$url.name == ncaa.team1[i]]
  score2 <- teams$LRMC.score[teams$url.name == ncaa.team2[i]]
  
  symbol <- "X"
  
  if(ncaa.winner[i] == 1 & score1 > score2) {
    correct <- correct + 1
    symbol <- "*"
  }

  if(ncaa.winner[i] == 2 & score2 > score1) {
    correct <- correct + 1
    symbol <- "*"
  }
  
  print(paste(symbol,paste(paste(ncaa.team1[i],"vs."),ncaa.team2[i])))
  
}

# correct picks in the NCAA tournement based on RPI
print("LRMC")
print(correct)
print(total)
print(correct/total)

# for each matchup in the NCAA Tournement, compute the number of
# times the widely used RPI model predicted the winner.
correct <- 0
total <- length(ncaa.team1)
for(i in 1:total) {
  
  score1 <- teams$RPI[teams$url.name == ncaa.team1[i]]
  score2 <- teams$RPI[teams$url.name == ncaa.team2[i]]
  
  score1 <- as.numeric(as.character(score1))
  score2 <- as.numeric(as.character(score2))
  
  symbol <- "X"
  
  if(ncaa.winner[i] == 1 & score1 > score2) {
    correct <- correct + 1
    symbol <- "*"
  }
  
  if(ncaa.winner[i] == 2 & score2 > score1) {
    correct <- correct + 1
    symbol <- "*"
  }
  
  print(paste(symbol,paste(paste(ncaa.team1[i],"vs."),ncaa.team2[i])))
  
}

# correct picks in the NCAA tournement based on RPI
print("RPI")
print(correct)
print(total)
print(correct/total)