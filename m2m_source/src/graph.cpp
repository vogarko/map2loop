/******************************************************************************
* A class for gml graphs generation.
*
* Author: Vitaliy Ogarko (2016).
*******************************************************************************/

#ifndef graph_cpp
#define graph_cpp

#include <iostream>
#include <fstream>
#include <algorithm>

#include "graph.h"
#include "converter_utils.h"
#include "data_reader.h"

namespace ConverterLib {

//! Convert integer to hex string.
template<typename T>
static std::string int_to_hex(T i)
{
  std::stringstream stream;
  stream << "0x"
         << std::setfill ('0') << std::setw(sizeof(T) * 2)
         << std::hex << i;
  return stream.str();
};

//! Convert RGB color value to a hexadecimal value.
static unsigned long createRGB(int r, int g, int b)
{
  // Store the appropriate bits of each color into an unsigned integer of at least 24 bits (like a long).
  return ((r & 0xff) << 16) + ((g & 0xff) << 8) + (b & 0xff);
};

static std::string RGB2HexColor(int color_r, int color_g, int color_b)
{
  unsigned long rgb = createRGB(color_r, color_g, color_b);
  std::string color = int_to_hex(rgb);
  color = "#" + color.substr(color.length() - 6, color.length());
  return color;
};

//! Creates color code (hexadecimal) based on the given scale, 0 <= scale <= 1.
static std::string CreateHexRGBString(double scale, bool lightColors = false)
{
  double cc = 0.;
  if (lightColors) {
      cc = 0.3;
  }

  // Red.
  const double color1_r = 1.0;
  const double color1_g = cc;
  const double color1_b = cc;

  // Green.
  const double color2_r = cc;
  const double color2_g = 1.0;
  const double color2_b = cc;

  // Blue.
  const double color3_r = cc;
  const double color3_g = cc;
  const double color3_b = 1.0;

  const double factor_color1 = std::max(scale - 0.5, 0.0);
  const double factor_color2 = 0.5 - std::fabs(0.5 - scale);
  const double factor_color3 = std::max(0.5 - scale, 0.0);

  // Use the color scheme that linearly and efficiently interpolates between three arbitrary colors.
  int color_r = (int)((color1_r * factor_color1 +
                       color2_r * factor_color2 +
                       color3_r * factor_color3) * 2.0 * 255.0);

  int color_g = (int)((color1_g * factor_color1 +
                       color2_g * factor_color2 +
                       color3_g * factor_color3) * 2.0 * 255.0);

  int color_b = (int)((color1_b * factor_color1 +
                       color2_b * factor_color2 +
                       color3_b * factor_color3) * 2.0 * 255.0);

  return RGB2HexColor(color_r, color_g, color_b);
};

//====================================================================================================
// Choose label_type to set a label inside of the graph node.
// label_type = "NO_LABEL": no label (mark graph block with a number).
// label_type = "UNIT_NAME": label by unit names.
// See http://docs.yworks.com/yfiles/doc/developers-guide/gml.html for reference on gml format.
//====================================================================================================
void GraphWriter::WriteGraph(const std::string &file_graph, const UnitContacts &contacts,
                             const std::string &label_type, bool exclude_sills,
                             int edge_width_type, const std::vector<double> &edge_width_categories,
                             int edge_direction_type,
                             const std::string &comments)
{
  // Sanity check.
  if (edge_width_categories.size() < 3)
  {
    std::cout << "At least 3 edge width categories requested!" << std::endl;
    exit(0);
  }

  std::cout << "Writing topology graph to a file: " << file_graph << std::endl;

  // Writing graph to a file.
  std::ofstream file;
  file.open(file_graph.c_str());

  if (comments != "") {
      // Write comment lines at the top (each line must start with hash).
      file << comments;
  }

  file <<
"Creator \"map2model-cpp\"\n\
graph [\n\
  hierarchic 1\n\
  directed 1\n";

  std::ofstream file_txt;
  file_txt.open((file_graph + ".txt").c_str());

  //-------------------------------------------------------------------------------------
  // (I) Writing graph nodes.

  // Build list of units that are present in contacts.
  Units filtered_units;

  for (UnitContacts::const_iterator it = contacts.begin(); it != contacts.end(); ++it)
  {
    filtered_units.insert(Units::value_type(it->unit1.name, it->unit1));
    filtered_units.insert(Units::value_type(it->unit2.name, it->unit2));
  }
  std::cout << "Number of units in the graph: " << filtered_units.size() << std::endl;

  // Build list of groups that are present in contacts.
  Groups filtered_groups;
  // Use negative id for groups, and positive for units, to keep them unique.
  int index = -1;

  for (Units::const_iterator it = filtered_units.begin(); it != filtered_units.end(); ++it)
  {
    filtered_groups.insert(Groups::value_type(it->second.group, index));
    index--;
  }
  std::cout << "Number of groups in the graph: " << filtered_groups.size() << std::endl;

  // Adding unit groups.
  for (Groups::const_iterator it = filtered_groups.begin(); it != filtered_groups.end(); ++it)
  {
    int id = it->second;
    std::string label = it->first;
    std::string color = "#FAFAFA";

    file <<
"  node [\n\
    id " << id << "\n\
    LabelGraphics [ text \"" << label << "\" anchor \"n\" fontStyle \"bold\" fontSize 14 ]\n\
    isGroup 1\n\
    graphics [ fill \"" << color << "\" ]\n\
  ]\n";

  }

  // Determine min/max length to set the unit color scale.
  double unit_min_length = 1e30;
  double unit_max_length = 0.;
  for (Units::const_iterator unit_it = filtered_units.begin(); unit_it != filtered_units.end(); ++unit_it) {
      if (unit_it->second.length > unit_max_length) {
          unit_max_length = unit_it->second.length;
      }
      if (unit_it->second.length < unit_min_length) {
          unit_min_length = unit_it->second.length;
      }
  }

  // Adding units.
  for (Units::const_iterator unit_it = filtered_units.begin(); unit_it != filtered_units.end(); ++unit_it)
  {
    int id = unit_it->second.id;

    // Determine the graph node color.
    std::string color = CreateHexRGBString((unit_it->second.length - unit_min_length) / (unit_max_length - unit_min_length), true);

    std::string label;
    if (label_type == "UNIT_NAME")
    {
      label = unit_it->first;
    } else // NO_LABEL
    {
      label = SSTR(id);
    }

    // Determine group id.
    Groups::const_iterator group_it = filtered_groups.find(unit_it->second.group);
    int gid = group_it->second;

    file <<
"  node [\n\
    id " << id << "\n\
    LabelGraphics [ text \"" << label << "\" fontSize 14 ]\n\
    gid " << gid << "\n\
    graphics [ fill \"" << color << "\" w 150 ]\n\
  ]\n";

    file_txt << id << " " << label << std::endl;
  }

  // Empty line separator between the header and the edges list.
  file_txt << std::endl;

  //-------------------------------------------------------------------------------------
  // (II) Writing graph edges.

  int source, target;
  std::string style, arrow, width;

  for (UnitContacts::const_iterator unit_contact_it = contacts.begin();
       unit_contact_it != contacts.end(); ++unit_contact_it)
  {
    // Exclude with sills, if needed.
    if (exclude_sills &&
        (unit_contact_it->unit1.is_sill || unit_contact_it->unit2.is_sill)) continue;

    // Direct graph edges according to the age.
    double age1, age2;

    if (edge_direction_type == 0)
    {
      age1 = unit_contact_it->unit1.min_age;
      age2 = unit_contact_it->unit2.min_age;
    }
    else if (edge_direction_type == 1)
    {
      age1 = unit_contact_it->unit1.max_age;
      age2 = unit_contact_it->unit2.max_age;
    }
    else
    {
      age1 = (unit_contact_it->unit1.min_age + unit_contact_it->unit1.max_age) / 2.;
      age2 = (unit_contact_it->unit2.min_age + unit_contact_it->unit2.max_age) / 2.;
    }

    int id1 = unit_contact_it->unit1.id;
    int id2 = unit_contact_it->unit2.id;

    // Setting source and target IDs.
    if (age1 <= age2)
    {
      source = id1;
      target = id2;
    } else
    {
      source = id2;
      target = id1;
    }

    // Set the line style.
    style = "line";

    // Set the arrow direction.
    if (age1 == age2)
    {
      arrow = "both";
    }
    else
    {
      arrow = "last";
    }

    // Set the line width.
    double length;
    if (edge_width_type == 0)
    {
      length = unit_contact_it->relative_length;
    } else
    {
      length = unit_contact_it->total_length;
    }

    if (length <= edge_width_categories[0])
    {
      width = "1";
    }
    else if (length <= edge_width_categories[1])
    {
      width = "3";
    }
    else if (length <= edge_width_categories[2])
    {
      width = "5";
    }
    else
    {
      width = "7";
    }

    std::string color = CreateHexRGBString(unit_contact_it->faults_length / unit_contact_it->total_length);

    file <<
"  edge [\n\
    source " << source << "\n\
    target " << target << "\n\
    graphics [ style \"" << style << "\" arrow \"" << arrow << "\" width " << width << " fill \"" << color << "\" ]\n\
  ]\n";

    file_txt << source << " " << target << " " << (arrow == "both") << std::endl;
  }

  file << "]";

  file.close();
  file_txt.close();
}

}

#endif
