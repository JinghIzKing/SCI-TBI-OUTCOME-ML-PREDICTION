library(dplyr)
df = read.csv('updated_combined.csv')

table(df$source)

colnames(df)

class(df$Injury.of.peripheral.nerves.of.thorax)

Pfunction <- function(df, col_name, value) {

  totalTBI <- 481535
  totalSCI <- 63843
  totalBoth <- 7072
  
 
  value_countTBI <- df %>% filter(source == "TBI" & !!sym(col_name) == value) %>% count()
  print(value_countTBI)
  value_countSCI <- df %>% filter(source == "SCI" & !!sym(col_name) == value) %>% count()
  print(value_countSCI)
  value_countBoth <- df %>% filter(source == "Both" & !!sym(col_name) == value) %>% count()
  print(value_countBoth)
  print('count end')

  cat("Count TBI:", value_countTBI$n, "Proportion TBI:", value_countTBI$n / totalTBI, "\n")
  cat("Count SCI:", value_countSCI$n, "Proportion SCI:", value_countSCI$n / totalSCI, "\n")
  cat("Count Both:", value_countBoth$n, "Proportion Both:", value_countBoth$n / totalBoth, "\n")
  
  p1_TBI <- value_countTBI$n / totalTBI
  p1_SCI <- value_countSCI$n / totalSCI
  p1_Both <- value_countBoth$n / totalBoth
  
  p_TBI_SCI <- (value_countTBI$n + value_countSCI$n) / (totalTBI + totalSCI)
  p_TBI_Both <- (value_countTBI$n + value_countBoth$n) / (totalTBI + totalBoth)
  p_SCI_Both <- (value_countSCI$n + value_countBoth$n) / (totalSCI + totalBoth)
  
  SE_TBI_SCI <- sqrt(p_TBI_SCI * (1 - p_TBI_SCI) * ((1 / totalTBI) + (1 / totalSCI)))
  SE_TBI_Both <- sqrt(p_TBI_Both * (1 - p_TBI_Both) * ((1 / totalTBI) + (1 / totalBoth)))
  SE_SCI_Both <- sqrt(p_SCI_Both * (1 - p_SCI_Both) * ((1 / totalSCI) + (1 / totalBoth)))
  
  z_TBI_SCI <- (p1_TBI - p1_SCI) / SE_TBI_SCI
  z_TBI_Both <- (p1_TBI - p1_Both) / SE_TBI_Both
  z_SCI_Both <- (p1_SCI - p1_Both) / SE_SCI_Both
  
  p_value_TBI_SCI <- 2 * (1 - pnorm(abs(z_TBI_SCI)))
  p_value_TBI_Both <- 2 * (1 - pnorm(abs(z_TBI_Both)))
  p_value_SCI_Both <- 2 * (1 - pnorm(abs(z_SCI_Both)))
  feature = col_name
  return(list(
    feature = feature,
    TBI = value_countTBI$n,
    SCI = value_countSCI$n,
    Both = value_countBoth$n,
    p_value_TBI_SCI = p_value_TBI_SCI,
    p_value_TBI_Both = p_value_TBI_Both,
    p_value_SCI_Both = p_value_SCI_Both
  ))
}

features <- c(
  "X.CHF", "Arr", "ValD", "PulmCD", "PVD", "HTNU", "HTNC", "Pa", "OND", "CPD",
  "DMU", "DMC", "HypoT", "RF", "LD", "PUD", "AIDS", "Lym", "Mets", "STU", "RA",
  "Coag", "Obe", "WL", "FED", "BLA", "DA", "AA", "DrugA", "Psych", "Dep",
  "Cervical", "Concussion.and.edema.of.cervical.spinal.cord",
  "Other.and.unspecified.injuries.of.cervical.spinal.cord",
  "X.Complete.lesion.of.cervical.spinal.cord",
  "Central.cord.syndrome.of.cervical.spinal.cord",
  "Anterior.cord.syndrome.of.cervical.spinal.cord",
  "Brown.Séquard.syndrome.of.cervical.spinal.cord",
  "Other.incomplete.lesions.of.cervical.spinal.cord",
  "Injury.of.nerve.root.of.cervical.spine", "Injury.of.brachial.plexus",
  "Injury.of.peripheral.nerves.of.neck", "Injury.of.cervical.sympathetic.nerves",
  "X.Injury.of.other.specified.nerves.of.neck", "Injury.of.unspecified.nerves.of.neck",
  "Lumbar.and.Sacral", "Concussion.and.edema.of.lumbar.and.sacral.spinal.cord",
  "Concussion.and.edema.of.sacral.spinal.cord",
  "Other.and.unspecified.injury.of.lumbar.and.sacral.spinal.cord",
  "Complete.lesion.of.lumbar.spinal.cord", "Incomplete.lesion.of.lumbar.spinal.cord",
  "Other.and.unspecified.injury.to.sacral.spinal.cord",
  "Injury.of.nerve.root.of.lumbar.and.sacral.spine", "Injury.of.cauda.equina",
  "Injury.of.lumbosacral.plexus",
  "Injury.of.lumbar..sacral.and.pelvic.sympathetic.nerves",
  "Injury.of.peripheral.nerve.s..at.abdomen..lower.back.and.pelvis.level",
  "Injury.of.other.nerves.at.abdomen..lower.back.and.pelvis.level",
  "Injury.of.unspecified.nerves.at.abdomen..lower.back.and.pelvis.level",
  "Thoracic", "Concussion.and.edema.of.thoracic.spinal.cord",
  "Other.and.unspecified.injuries.of.thoracic.spinal.cord",
  "Complete.lesion.of.thoracic.spinal.cord", "Anterior.cord.syndrome.of.thoracic.spinal.cord",
  "Brown.Séquard.syndrome.of.thoracic.spinal.cord",
  "Other.incomplete.lesions.of.thoracic.spinal.cord",
  "Injury.of.nerve.root.of.thoracic.spine", "Injury.of.peripheral.nerves.of.thorax",
  "Injury.of.thoracic.sympathetic.nervous.system",
  "Injury.of.other.specified.nerves.of.thorax", "Injury.of.unspecified.nerve.of.thorax",
  "Neurological.Complications", "Musculoskeletal...Mobility.Issues",
  "Pain...Discomfort", "Skin...Pressure.Related.Conditions",
  "Circulatory...Vascular.Issues", "Urological...Gastrointestinal.Issues",
  "Respiratory...Pulmonary.Issues", "Post.Surgical...Structural.Issues",
  "Mental.Health...Psychological.Impact", "Other.Regulatory.Issues",
  "Sexual...Reproductive.Issues", "Concussion", "Epidural.hemorrhage",
  "Unspecified.intracranial.injury", "Traumatic.cerebral.edema",
  "Diffuse.traumatic.brain.injury", "Traumatic.subdural.hemorrhage",
  "Traumatic.subarachnoid.hemorrhage", "Other.specified.intracranial.injuries",
  "Traumatic.brain.compression.and.herniation", "Focal.traumatic.brain.injury",
  "Surgical.Interventions", "Structural.Pathology", "Infectious.Pathology",
  "Hematologic.Pathology", "Neurological.Pathology.Acute",
  "Neurological.Pathology.Chronic.Progressive", "Emotional.Behavioral.Cognitive"
)

library(writexl)
library(rlang)


all_results <- list()





for (f in features) {
  
  row <- Pfunction(df, f, "1")
  
  all_results[[f]] <- row
}


final_results_df <- bind_rows(all_results)

write_xlsx(final_results_df, "output8.xlsx")




