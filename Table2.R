library(dplyr)
df = read.csv('hot_encoded.csv')

table(df$source)

colnames(df)

class(df$Injury.of.peripheral.nerves.of.thorax)

Pfunction <- function(df, col_name, value) {  
  totalTBI <- 473123  
  totalSCI <- 56177  
  totalBoth <- 23150  
  
  value_countTBI <- df %>% filter(source == "TBI", !!sym(col_name) == value) %>% count()
  value_countSCI <- df %>% filter(source == "SCI", !!sym(col_name) == value) %>% count()
  value_countBoth <- df %>% filter(source == "Both", !!sym(col_name) == value) %>% count()
  
  good_n_TBI <- ifelse(nrow(value_countTBI) == 0, 0, value_countTBI$n)
  good_n_SCI <- ifelse(nrow(value_countSCI) == 0, 0, value_countSCI$n)
  good_n_Both <- ifelse(nrow(value_countBoth) == 0, 0, value_countBoth$n)
  
  # Run proportion tests
  test_TBI_SCI <- prop.test(x = c(good_n_TBI, good_n_SCI), n = c(totalTBI, totalSCI), correct = FALSE)
  test_TBI_Both <- prop.test(x = c(good_n_TBI, good_n_Both), n = c(totalTBI, totalBoth), correct = FALSE)
  test_SCI_Both <- prop.test(x = c(good_n_SCI, good_n_Both), n = c(totalSCI, totalBoth), correct = FALSE)
  
  # Return results in a data.frame
  return(data.frame(
    feature = col_name,
    value = value,
    count_TBI = good_n_TBI,
    count_SCI = good_n_SCI,
    count_Both = good_n_Both,
    prop_TBI = good_n_TBI / totalTBI,
    prop_SCI = good_n_SCI / totalSCI,
    prop_Both = good_n_Both / totalBoth,
    p_value_TBI_SCI = test_TBI_SCI$p.value,
    p_value_TBI_Both = test_TBI_Both$p.value,
    p_value_SCI_Both = test_SCI_Both$p.value
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

write_xlsx(final_results_df, "output1.2.xlsx")




