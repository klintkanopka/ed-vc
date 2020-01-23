library(tidyverse)
conflict_prefer('filter', 'dplyr')

orgs <- read_csv('data/organizations.csv')
invs <- read_csv('data/edtech_invs.csv')

d_orgs <- orgs %>%
  filter(primary_role == 'investor') %>%
  filter(!is.na(permalink)) %>%
  mutate(exits = case_when(
    is.na(num_exits) ~ 0,
    TRUE ~ num_exits
  ))

d_invs <- invs %>%
  filter(!is.na(permalink)) %>%
  mutate(exits = case_when(
    is.na(num_exits) ~ 0,
    TRUE ~ num_exits
  ))

ggplot() +
  geom_density(data = d_orgs, 
               aes(x = exits, 
                   fill = 'All Investors'),
               color = 'darkorchid',
               alpha = 0.4) +
  geom_density(data = d_invs, 
               aes(x = exits,
                   fill = 'EdTech Investors'),
               color = 'forestgreen',
               alpha = 0.4) +
  scale_fill_manual(name = 'Investor Type', values = c('All Investors' = 'dark orchid',
                                                       'EdTech Investors' = 'forestgreen')) +
  ggtitle('Investors who fund EdTechs tend to have more successful exits
          (mean 12.96 exits vs. mean 1.33 exits among all investors)') +
  theme_bw()

ggsave('plots/num_exits.png')

mean(d_orgs$exits)
mean(d_invs$exits)

cons <- read_csv('data/edtech_cons.csv')

d <- cons %>%
  group_by(investor_permalink) %>%
  filter(!is.na(investor_permalink)) %>%
  summarize(n = n())

ggplot(d, aes(x = n)) +
  geom_density(fill = 'forestgreen', color = 'forestgreen', alpha = 0.4) +
  theme_bw() + 
  xlab('Number of EdTech Investments') +
  ylab('Density') +
  ggtitle('Most investors only fund one or two EdTechs (mean = 1.5)')

ggsave('plots/num_investments.png')

cons %>%
  group_by(funding_type) %>%
  summarize(n = n()) %>%
  ggplot(aes(x = reorder(funding_type, n), y = n)) +
  geom_point(stat = 'identity', color = 'forestgreen') + 
  coord_flip() +
  theme_bw() +
  ggtitle("Most EdTech funding is seed or venture funding") +
  xlab('Funding Type') +
  ylab('n')

ggsave('plots/funding_type.png')

d %>%
  transmute(permalink = investor_permalink,
              n = n) %>%
  inner_join(d_invs, by = 'permalink') %>%
  select(permalink, n, exits) %>%
  ggplot(aes(x = n, y = exits)) +
  geom_point(color = 'forestgreen') +
  geom_smooth(method='lm', 
              se=FALSE,
              color = 'indianred') +
  theme_bw() + 
  ggtitle('Making more EdTech investments is associated with more successful exits') +
  xlab('Number of EdTech investments') + 
  ylab('Number of exits')

ggsave('plots/exitsvsinvs.png')
